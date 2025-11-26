import sys
import cv2
import numpy as np
import pyttsx3
import threading
import chess
import chess.pgn
import time
import webbrowser
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QCheckBox, QSlider, QGroupBox, QGridLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage

# --- CONFIGURATION ---
CAMERA_ID = 0
EDGE_THRESHOLD = 300  # Increased to reduce false positives
EDGE_DIFFERENCE_THRESHOLD = 200  # Minimum difference from empty reference
AVAILABLE_CAMERAS = []  # Will be populated at runtime

# --- AUDIO ---
def speak(text):
    """Non-blocking speech"""
    threading.Thread(target=lambda: _speak_thread(text)).start()

def _speak_thread(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Audio error: {e}")

def expand_chess_text(san):
    """Convert SAN (e.g. Nf3) to spoken text"""
    text = san.replace('N', 'Knight ').replace('B', 'Bishop ').replace('R', 'Rook ').replace('Q', 'Queen ').replace('K', 'King ')
    if text[0].islower():
        text = "Pawn to " + text
    text = text.replace('x', ' captures ').replace('+', ' check').replace('#', ' checkmate')
    text = text.replace('O-O-O', 'Long Castles').replace('O-O', 'Short Castles')
    return text

# --- LOGIC ---
class OccupancyChessSystem:
    def __init__(self, debounce_time=1.5):
        self.board = chess.Board()
        self.debounce_time = debounce_time
        self.stable_start_time = 0
        self.last_occupancy_grid = None
        self.expected_occupancy = self._get_board_occupancy(self.board)
        self.last_move = None  # Track last move for visualization
        self.move_list = []  # Track Move objects for PGN export

    def sync_board(self, visual_occupancy_grid):
        """Initialize board from visual setup (standard starting position assumed)"""
        log_msgs = []
        log_msgs.append("Syncing internal board to standard starting position...")
        
        # Reset to standard starting position
        self.board = chess.Board()
        
        self.expected_occupancy = self._get_board_occupancy(self.board)
        self.last_occupancy_grid = visual_occupancy_grid
        log_msgs.append("Board Sync Complete. Assuming standard starting position.")
        return log_msgs

    def undo_last_move(self):
        """Undo the most recent move if possible."""
        if not self.move_list:
            return False
        # Pop last move from board
        try:
            self.board.pop()
        except IndexError:
            # No move to pop
            return False
        # Remove from move list
        self.move_list.pop()
        # Update last_move
        if self.move_list:
            self.last_move = self.move_list[-1]
        else:
            self.last_move = None
        return True

    def _get_board_occupancy(self, board):
        grid = [[False]*8 for _ in range(8)]
        for r in range(8):
            for c in range(8):
                rank = 7 - r
                file = c
                square = chess.square(file, rank)
                if board.piece_at(square) is not None:
                    grid[r][c] = True
        return grid

    def update(self, detected_occupancy_grid, debug_mode=False, no_turn_mode=False):
        current_time = time.time()
        if self.last_occupancy_grid is None:
            self.last_occupancy_grid = detected_occupancy_grid
            self.stable_start_time = current_time
            return None, []

        logs = []
        if detected_occupancy_grid == self.last_occupancy_grid:
            if current_time - self.stable_start_time > self.debounce_time:
                expected = self._get_board_occupancy(self.board)
                if detected_occupancy_grid != expected:
                    logs.append(f"DEBUG: Stable State Differs. Expected {sum([sum(r) for r in expected])}, Got {sum([sum(r) for r in detected_occupancy_grid])}")
                    
                    move = self._infer_move(expected, detected_occupancy_grid, logs, debug_mode)
                    
                    if move:
                        # Check No Turn Mode
                        if no_turn_mode and not debug_mode:
                            piece = self.board.piece_at(move.from_square)
                            if piece and piece.color != self.board.turn:
                                logs.append(f"No Turn Mode: Switching turn to {'White' if piece.color else 'Black'}")
                                self.board.turn = piece.color
                        
                        san = "Move"
                        if not debug_mode:
                            if move in self.board.legal_moves:
                                try:
                                    san = self.board.san(move)
                                    self.board.push(move)
                                    self.last_move = move  # Track last move
                                    self.move_list.append(move)  # Store Move object
                                except:
                                    san = move.uci()
                                    self.board.push(move)
                                    self.last_move = move
                                    self.move_list.append(san)
                                self.stable_start_time = current_time 
                                return san, logs
                            else:
                                logs.append(f"Illegal Move Detected: {move.uci()}")
                                speak("Illegal Move")
                                self.stable_start_time = current_time
                                return None, logs
                        else:
                            # Debug mode: Force the move
                            san = f"Force {move.uci()}"
                            piece = self.board.remove_piece_at(move.from_square)
                            if piece:
                                self.board.set_piece_at(move.to_square, piece)
                            else:
                                logs.append("DEBUG: Tried to move non-existent piece!")

                            self.stable_start_time = current_time 
                            return san, logs
                    else:
                        # Diff logging
                        diffs = []
                        for r in range(8):
                            for c in range(8):
                                if expected[r][c] != detected_occupancy_grid[r][c]:
                                    rank = 7 - r
                                    file = c
                                    sq_name = chess.square_name(chess.square(file, rank))
                                    state = "Occ" if detected_occupancy_grid[r][c] else "Emp"
                                    exp = "Occ" if expected[r][c] else "Emp"
                                    diffs.append(f"{sq_name}: {exp}->{state}")
                        if diffs:
                            logs.append(f"DEBUG: Diffs: {', '.join(diffs)}")
                        
                        self.stable_start_time = current_time
        else:
            self.last_occupancy_grid = detected_occupancy_grid
            self.stable_start_time = current_time
            
        return None, logs

    def _infer_move(self, expected_grid, visual_grid, logs, debug_mode=False):
        sources = []
        targets = []
        for r in range(8):
            for c in range(8):
                was_occ = expected_grid[r][c]
                is_occ = visual_grid[r][c]
                if was_occ and not is_occ:
                    sources.append((r, c))
                elif not was_occ and is_occ:
                    targets.append((r, c))
                    
        def to_square(r, c):
            return chess.square(c, 7 - r)

        # Case 1: Standard Move (1 Source, 1 Target)
        if len(sources) == 1 and len(targets) == 1:
            src = to_square(*sources[0])
            dst = to_square(*targets[0])
            move = chess.Move(src, dst)
            
            if debug_mode:
                return move 

            # Check for promotion
            if self.board.piece_at(src) and self.board.piece_at(src).piece_type == chess.PAWN:
                if chess.square_rank(dst) in [0, 7]:
                    move = chess.Move(src, dst, promotion=chess.QUEEN)
            
            return move
                
        # Case 2: Capture (1 Source, 0 Targets)
        # Visually: Source becomes empty, Target remains occupied (so no change in target state)
        elif len(sources) == 1 and len(targets) == 0:
            src = to_square(*sources[0])
            if debug_mode:
                logs.append("DEBUG: Capture detected (Source disappeared). Target unknown in Debug Mode.")
                return None

            # Find legal moves from this source that are captures
            candidates = []
            for m in self.board.legal_moves:
                if m.from_square == src and self.board.is_capture(m):
                    # For a capture, the destination must be occupied in the expected grid
                    # (unless en passant, which is handled separately or treated as capture)
                    # We verify that the visual grid shows the destination as OCCUPIED (which it should, as it was before)
                    dst_r = 7 - chess.square_rank(m.to_square)
                    dst_c = chess.square_file(m.to_square)
                    if visual_grid[dst_r][dst_c]:
                        candidates.append(m)
            
            if len(candidates) == 1:
                move = candidates[0]
                # Check for promotion on capture
                if self.board.piece_at(src).piece_type == chess.PAWN and chess.square_rank(move.to_square) in [0, 7]:
                    move.promotion = chess.QUEEN
                return move
            elif len(candidates) > 1:
                # Ambiguity Resolution: Material Gain Heuristic
                # Choose the move that captures the highest value piece
                best_move = None
                max_val = -1
                
                piece_values = {
                    chess.QUEEN: 9, chess.ROOK: 5, chess.BISHOP: 3, chess.KNIGHT: 3, chess.PAWN: 1
                }
                
                logs.append(f"Ambiguous capture from {chess.square_name(src)}. Candidates: {[m.uci() for m in candidates]}")
                
                for m in candidates:
                    captured_piece = self.board.piece_at(m.to_square)
                    val = 0
                    if captured_piece:
                        val = piece_values.get(captured_piece.piece_type, 0)
                    
                    if val > max_val:
                        max_val = val
                        best_move = m
                
                if best_move:
                    logs.append(f"Resolved ambiguity: Choosing {best_move.uci()} (Captures value {max_val})")
                    # Check for promotion on resolved capture
                    if self.board.piece_at(src).piece_type == chess.PAWN and chess.square_rank(best_move.to_square) in [0, 7]:
                        best_move.promotion = chess.QUEEN
                    return best_move
                else:
                    return None

        # Case 3: Castling (2 Sources, 2 Targets)
        elif len(sources) == 2 and len(targets) == 2:
            for move in self.board.legal_moves:
                if self.board.is_castling(move):
                    self.board.push(move)
                    temp_occ = self._get_board_occupancy(self.board)
                    self.board.pop()
                    if temp_occ == visual_grid:
                        return move

        # Case 4: En Passant (2 Sources, 1 Target)
        # Pawn moves to empty square (Target), but captures piece on another square (2nd Source)
        elif len(sources) == 2 and len(targets) == 1:
             for move in self.board.legal_moves:
                if self.board.is_en_passant(move):
                    self.board.push(move)
                    temp_occ = self._get_board_occupancy(self.board)
                    self.board.pop()
                    if temp_occ == visual_grid:
                        return move
        return None

    def export_pgn(self, filename=None):
        """Export game to PGN format"""
        import datetime
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.pgn"
        
        game = chess.pgn.Game()
        game.headers["Event"] = "BlindChess Vision Game"
        game.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = "Player"
        game.headers["Black"] = "Player"
        
        node = game
        for move in self.move_list:
            if move:
                node = node.add_variation(move)
        
        with open(filename, 'w') as f:
            f.write(str(game))
        
        return filename
    
    def get_pgn_string(self):
        """Get PGN as string for API upload"""
        import datetime
        game = chess.pgn.Game()
        game.headers["Event"] = "BlindChess Vision Game"
        game.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = "Player"
        game.headers["Black"] = "Player"
        
        node = game
        for move in self.move_list:
            if move:
                node = node.add_variation(move)
        
        return str(game)

# --- WORKER THREAD ---
class VisionWorker(QThread):
    frame_update = pyqtSignal(QImage, QImage)
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.state = "WAITING"
        self.calibration_matrix = None
        self.chess_system = OccupancyChessSystem()
        self.cap = None
        self.debug_mode = False
        self.no_turn_mode = False
        self.empty_board_reference = None
        
        # Configurable edge detection parameters
        self.edge_threshold = EDGE_THRESHOLD
        self.edge_diff_threshold = EDGE_DIFFERENCE_THRESHOLD
        self.canny_low = 100
        self.canny_high = 200
        self.blur_kernel = 5

    def set_debug_mode(self, enabled):
        self.debug_mode = enabled
        self.log_message.emit(f"Debug Mode: {enabled}")

    def set_no_turn_mode(self, enabled):
        self.no_turn_mode = enabled
        self.log_message.emit(f"No Turn Mode: {enabled}")

    def _apply_calibration(self, corners):
        base_indices = [0, 6, 48, 42]
        shifted_indices = base_indices[:]
        for _ in range(self.rotation_index):
            shifted_indices = [shifted_indices[-1]] + shifted_indices[:-1]
            
        src_pts = np.float32([corners[i] for i in shifted_indices])
        dst_pts = np.float32([[200, 200], [800, 200], [800, 800], [200, 800]])
        
        self.calibration_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        self.state = "SETUP"
        self.last_raw_corners = corners

    def command_rotate(self):
        self.rotation_index = (self.rotation_index + 1) % 4
        deg = self.rotation_index * 90
        self.log_message.emit(f"Rotated Board {deg}°")
        
        if self.last_raw_corners is not None:
            self._apply_calibration(self.last_raw_corners)

    def detect_occupancy_edge_based(self, warped):
        """Detect occupancy using edge density (no AI needed)"""
        occupancy_grid = [[False]*8 for _ in range(8)]
        
        # Convert to grayscale
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)
        
        # Detect edges with configurable thresholds
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        
        # Apply morphological operations to connect nearby edges
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # For each square, count edges
        for r in range(8):
            for c in range(8):
                x1 = 100 + c * 100 + 10  # Add margin
                y1 = 100 + r * 100 + 10
                x2 = x1 + 80  # Reduce square size to avoid border edges
                y2 = y1 + 80
                
                square_edges = edges[y1:y2, x1:x2]
                edge_count = np.sum(square_edges > 0)
                
                # If using empty board reference, compare
                if self.empty_board_reference is not None:
                    ref_square = self.empty_board_reference[y1:y2, x1:x2]
                    ref_edge_count = np.sum(ref_square > 0)
                    # Occupied if significantly more edges than empty
                    occupancy_grid[r][c] = (edge_count - ref_edge_count) > self.edge_diff_threshold
                else:
                    # Simple threshold
                    occupancy_grid[r][c] = edge_count > self.edge_threshold
                    
        return occupancy_grid

    def run(self):
        self.log_message.emit("System Ready (No AI Model Required)")
        
        self.cap = cv2.VideoCapture(CAMERA_ID)
        if not self.cap.isOpened():
            self.log_message.emit("Error: Could not open camera.")
            return

        self.log_message.emit("System Ready. Please Calibrate.")
        speak("System Ready. Please Calibrate.")
        
        self.request_calibration = False
        self.rotation_index = 0
        self.last_raw_corners = None

        while self.running:
            ret, frame = self.cap.read()
            if not ret: break

            if self.request_calibration:
                corners = self.get_board_corners(frame)
                if corners is not None:
                    self._apply_calibration(corners)
                    
                    # Capture empty board reference with same processing
                    warped = cv2.warpPerspective(frame, self.calibration_matrix, (1000, 1000))
                    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
                    blurred = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)
                    edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
                    kernel = np.ones((3, 3), np.uint8)
                    self.empty_board_reference = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
                    
                    self.log_message.emit("Calibrated Successfully. Empty board reference captured.")
                    speak("Calibrated.")
                else:
                    self.log_message.emit("Calibration Failed: Board not found.")
                    speak("Board not found.")
                self.request_calibration = False

            if self.state == "WAITING":
                corners = self.get_board_corners(frame)
                if corners is not None:
                    cv2.drawChessboardCorners(frame, (7,7), corners, True)
                self.frame_update.emit(self.convert_cv_qt(frame), self.convert_cv_qt(np.zeros((300,300,3), np.uint8)))

            elif self.state in ["SETUP", "GAME"]:
                if self.calibration_matrix is not None:
                    warped = cv2.warpPerspective(frame, self.calibration_matrix, (1000, 1000))
                    
                    # Edge-based occupancy detection
                    occupancy_grid = self.detect_occupancy_edge_based(warped)
                    
                    # Visualization
                    annotated_warped = warped.copy()
                    self.draw_grid_and_occupancy(annotated_warped, occupancy_grid, self.chess_system.last_move)
                    
                    self.last_grid = occupancy_grid
                    
                    if self.state == "GAME":
                        move_san, logs = self.chess_system.update(occupancy_grid, self.debug_mode, self.no_turn_mode)
                        for log in logs: self.log_message.emit(log)
                        if move_san:
                            spoken = expand_chess_text(move_san)
                            speak(spoken)
                            self.log_message.emit(f"MOVE: {move_san} -> {spoken}")
                            self.log_message.emit(str(self.chess_system.board))

                    self.frame_update.emit(self.convert_cv_qt(frame), self.convert_cv_qt(annotated_warped))

            time.sleep(0.01)
        self.cap.release()

    def get_board_corners(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (7,7), None)
        if ret: return corners
        return None

    def command_calibrate(self):
        self.request_calibration = True

    def command_start_game(self):
        self.state = "GAME"
        if hasattr(self, 'last_grid'):
            logs = self.chess_system.sync_board(self.last_grid)
            for log in logs:
                self.log_message.emit(log)
            speak("Game Started.")

    def command_stop_game(self):
        self.state = "SETUP"
        self.chess_system = OccupancyChessSystem()
        speak("Game Stopped. System Reset.")

    def command_undo(self):
        """Undo the last move in the chess system"""
        if self.state == "GAME":
            undone = self.chess_system.undo_last_move()
            if undone:
                self.log_message.emit("Undo performed")
                speak("Undo")
                # Force update of visualization
                if hasattr(self, 'last_grid'):
                    # We don't need to re-sync, just let the next frame update handle it
                    pass
            else:
                self.log_message.emit("No moves to undo")
                speak("Cannot undo")

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return convert_to_Qt_format.scaled(400, 400, Qt.KeepAspectRatio)

    def draw_grid_and_occupancy(self, img, grid, last_move=None):
        # Lichess Brown Theme Colors (BGR)
        # Light: #F0D9B5 -> (181, 217, 240)
        # Dark:  #B58863 -> (99, 136, 181)
        COLOR_LIGHT = (181, 217, 240)
        COLOR_DARK = (99, 136, 181)
        
        # Overwrite image with board background
        # We use the 100-900 range for the board (800x800)
        # Fill background (margin) with dark grey
        img[:] = (30, 30, 30)
        
        # Draw Board Squares
        for r in range(8):
            for c in range(8):
                x1 = 100 + c * 100
                y1 = 100 + r * 100
                x2 = x1 + 100
                y2 = y1 + 100
                
                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
                
                # Draw Coordinates (Lichess style: Rank on Left-Top of Light squares, File on Right-Bottom of Dark squares? 
                # Actually Lichess puts them on the edge squares)
                font_scale = 0.5
                font_color = COLOR_DARK if (r + c) % 2 == 0 else COLOR_LIGHT
                
                # Rank Labels (1-8) on the left edge (File 'a', c=0)
                if c == 0:
                    rank_label = str(8 - r)
                    cv2.putText(img, rank_label, (x1 + 5, y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 1)
                    
                # File Labels (a-h) on the bottom edge (Rank 1, r=7)
                if r == 7:
                    file_label = chr(ord('a') + c)
                    cv2.putText(img, file_label, (x2 - 20, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 1)

        # Highlight last move
        if last_move:
            from_square = last_move.from_square
            to_square = last_move.to_square
            
            # Highlight color (Yellow-ish transparent look? We can't do alpha easily in OpenCV without overlay)
            # Let's just draw a solid color mixed or a border. 
            # Lichess uses a yellow highlight.
            # BGR: (100, 255, 255) - Yellow
            HIGHLIGHT_COLOR = (100, 255, 255) # Yellow
            
            for sq in [from_square, to_square]:
                f = chess.square_file(sq)
                r = 7 - chess.square_rank(sq)
                x1 = 100 + f * 100
                y1 = 100 + r * 100
                
                # Draw a semi-transparent highlight by blending
                sub_img = img[y1:y1+100, x1:x1+100]
                colored_rect = np.zeros(sub_img.shape, dtype=np.uint8)
                colored_rect[:] = HIGHLIGHT_COLOR
                res = cv2.addWeighted(sub_img, 0.6, colored_rect, 0.4, 1.0)
                img[y1:y1+100, x1:x1+100] = res

        # Draw Pieces or Occupancy Dots using PIL
        from PIL import Image, ImageDraw, ImageFont
        
        # Convert to PIL Image
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        # Try to load a font that supports chess symbols
        try:
            # macOS standard font
            font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
            font = ImageFont.truetype(font_path, 80) # Larger font for pieces
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", 80)
            except:
                font = ImageFont.load_default()

        # Unicode Piece Map
        piece_map = {
            chess.WHITE: {
                chess.KING: "♔", chess.QUEEN: "♕", chess.ROOK: "♖",
                chess.BISHOP: "♗", chess.KNIGHT: "♘", chess.PAWN: "♙"
            },
            chess.BLACK: {
                chess.KING: "♚", chess.QUEEN: "♛", chess.ROOK: "♜",
                chess.BISHOP: "♝", chess.KNIGHT: "♞", chess.PAWN: "♟"
            }
        }

        for r in range(8):
            for c in range(8):
                # Check internal board state for piece identity
                rank = 7 - r
                file = c
                square = chess.square(file, rank)
                piece = self.chess_system.board.piece_at(square)
                
                cx = int(100 + c * 100 + 50)
                cy = int(100 + r * 100 + 50)

                if piece:
                    # Draw Unicode Piece
                    text = piece_map[piece.color].get(piece.piece_type, '?')
                    
                    # Color: White pieces White, Black pieces Black
                    text_color = (255, 255, 255) if piece.color == chess.WHITE else (0, 0, 0)
                    
                    # No background circle needed for digital board, looks cleaner
                    # Maybe a slight shadow for white pieces if on light square?
                    # Actually, just drawing them is fine.
                    
                    # Center text
                    bbox = draw.textbbox((0, 0), text, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    tx = cx - w / 2
                    ty = cy - h / 2 - 10 
                    
                    draw.text((tx, ty), text, font=font, fill=text_color)
                
                # ALWAYS draw detection status if occupied visually
                if grid[r][c]:
                    # Draw small Green Dot to indicate "Visual Detection"
                    # Position: Top-Right of the square (to not obscure piece too much?)
                    # Or Bottom-Right as before.
                    dx = cx + 35
                    dy = cy + 35
                    draw.ellipse((dx-10, dy-10, dx+10, dy+10), fill=(0, 255, 0), outline=(0,0,0))

        # Draw Turn Indicator on PIL image
        turn_text = "White's Turn" if self.chess_system.board.turn == chess.WHITE else "Black's Turn"
        turn_color = (255, 255, 255) if self.chess_system.board.turn == chess.WHITE else (255, 0, 0) # Red for Black turn
        try:
            font_small = ImageFont.truetype("Arial.ttf", 40)
        except:
            font_small = ImageFont.load_default()
        draw.text((50, 20), turn_text, font=font_small, fill=turn_color)

        # Convert back to OpenCV
        img[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# --- GUI ---
class ClickableLabel(QLabel):
    clicked = pyqtSignal(int, int)
    def mousePressEvent(self, event):
        self.clicked.emit(event.x(), event.y())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlindChess Vision (No AI)")
        self.setGeometry(100, 100, 1200, 900)

        main_layout = QVBoxLayout()
        video_layout = QHBoxLayout()
        controls_layout = QHBoxLayout()
        params_layout = QHBoxLayout()

        self.raw_video_label = ClickableLabel("Raw Video")
        self.warped_video_label = QLabel("Warped View")
        self.raw_video_label.setFixedSize(400, 400)
        self.warped_video_label.setFixedSize(400, 400)
        self.raw_video_label.setStyleSheet("background-color: black;")
        self.warped_video_label.setStyleSheet("background-color: black;")
        
        video_layout.addWidget(self.raw_video_label)
        video_layout.addWidget(self.warped_video_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace;")

        # Control Buttons
        self.btn_calibrate = QPushButton("Calibrate (Empty Board)")
        self.btn_rotate = QPushButton("Rotate 90°")
        self.btn_start = QPushButton("Start Game")
        self.btn_stop = QPushButton("Stop Game")
        self.btn_export = QPushButton("Export PGN")
        self.btn_undo = QPushButton("Undo Move")
        self.chk_debug = QCheckBox("Debug: Ignore Rules")
        self.chk_noturn = QCheckBox("No Turn Mode")
        
        self.btn_calibrate.clicked.connect(self.calibrate)
        self.btn_rotate.clicked.connect(self.rotate)
        self.btn_start.clicked.connect(self.start_game)
        self.btn_stop.clicked.connect(self.stop_game)
        self.btn_export.clicked.connect(self.export_pgn)
        self.btn_undo.clicked.connect(self.undo_move)
        self.chk_debug.stateChanged.connect(self.toggle_debug)
        self.chk_noturn.stateChanged.connect(self.toggle_noturn)
        
        controls_layout.addWidget(self.btn_calibrate)
        controls_layout.addWidget(self.btn_rotate)
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.btn_export)
        controls_layout.addWidget(self.btn_undo)
        controls_layout.addWidget(self.chk_debug)
        controls_layout.addWidget(self.chk_noturn)

        # Parameter Controls
        params_group = QGroupBox("Edge Detection Parameters")
        params_grid = QGridLayout()
        params_grid.setColumnStretch(1, 3)  # Make slider column wider
        params_grid.setSpacing(10)
        
        # Edge Threshold
        self.lbl_edge_thresh = QLabel(f"Edge Threshold: {EDGE_THRESHOLD}")
        self.lbl_edge_thresh.setMinimumWidth(180)
        self.slider_edge_thresh = QSlider(Qt.Horizontal)
        self.slider_edge_thresh.setMinimum(50)
        self.slider_edge_thresh.setMaximum(1000)
        self.slider_edge_thresh.setValue(EDGE_THRESHOLD)
        self.slider_edge_thresh.setMinimumWidth(300)
        self.slider_edge_thresh.valueChanged.connect(self.update_edge_threshold)
        params_grid.addWidget(self.lbl_edge_thresh, 0, 0)
        params_grid.addWidget(self.slider_edge_thresh, 0, 1)
        
        # Edge Difference Threshold
        self.lbl_diff_thresh = QLabel(f"Diff Threshold: {EDGE_DIFFERENCE_THRESHOLD}")
        self.lbl_diff_thresh.setMinimumWidth(180)
        self.slider_diff_thresh = QSlider(Qt.Horizontal)
        self.slider_diff_thresh.setMinimum(50)
        self.slider_diff_thresh.setMaximum(500)
        self.slider_diff_thresh.setValue(EDGE_DIFFERENCE_THRESHOLD)
        self.slider_diff_thresh.setMinimumWidth(300)
        self.slider_diff_thresh.valueChanged.connect(self.update_diff_threshold)
        params_grid.addWidget(self.lbl_diff_thresh, 1, 0)
        params_grid.addWidget(self.slider_diff_thresh, 1, 1)
        
        # Canny Low
        self.lbl_canny_low = QLabel("Canny Low: 100")
        self.lbl_canny_low.setMinimumWidth(180)
        self.slider_canny_low = QSlider(Qt.Horizontal)
        self.slider_canny_low.setMinimum(10)
        self.slider_canny_low.setMaximum(200)
        self.slider_canny_low.setValue(100)
        self.slider_canny_low.setMinimumWidth(300)
        self.slider_canny_low.valueChanged.connect(self.update_canny_low)
        params_grid.addWidget(self.lbl_canny_low, 2, 0)
        params_grid.addWidget(self.slider_canny_low, 2, 1)
        
        # Canny High
        self.lbl_canny_high = QLabel("Canny High: 200")
        self.lbl_canny_high.setMinimumWidth(180)
        self.slider_canny_high = QSlider(Qt.Horizontal)
        self.slider_canny_high.setMinimum(50)
        self.slider_canny_high.setMaximum(400)
        self.slider_canny_high.setValue(200)
        self.slider_canny_high.setMinimumWidth(300)
        self.slider_canny_high.valueChanged.connect(self.update_canny_high)
        params_grid.addWidget(self.lbl_canny_high, 3, 0)
        params_grid.addWidget(self.slider_canny_high, 3, 1)
        
        # Blur Kernel
        self.lbl_blur = QLabel("Blur Kernel: 5")
        self.lbl_blur.setMinimumWidth(180)
        self.slider_blur = QSlider(Qt.Horizontal)
        self.slider_blur.setMinimum(1)
        self.slider_blur.setMaximum(15)
        self.slider_blur.setValue(5)
        self.slider_blur.setMinimumWidth(300)
        self.slider_blur.setSingleStep(2)
        self.slider_blur.valueChanged.connect(self.update_blur)
        params_grid.addWidget(self.lbl_blur, 4, 0)
        params_grid.addWidget(self.slider_blur, 4, 1)
        
        params_group.setLayout(params_grid)
        params_group.setMaximumHeight(250)
        params_layout.addWidget(params_group)
        params_layout.addStretch()

        main_layout.addLayout(video_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(params_layout)
        main_layout.addWidget(self.log_text)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.worker = VisionWorker()
        self.worker.frame_update.connect(self.update_image)
        self.worker.log_message.connect(self.append_log)
        self.worker.start()

    def update_edge_threshold(self, value):
        self.lbl_edge_thresh.setText(f"Edge Threshold: {value}")
        self.worker.edge_threshold = value
        
    def update_diff_threshold(self, value):
        self.lbl_diff_thresh.setText(f"Diff Threshold: {value}")
        self.worker.edge_diff_threshold = value
        
    def update_canny_low(self, value):
        self.lbl_canny_low.setText(f"Canny Low: {value}")
        self.worker.canny_low = value
        
    def update_canny_high(self, value):
        self.lbl_canny_high.setText(f"Canny High: {value}")
        self.worker.canny_high = value
        
    def update_blur(self, value):
        # Ensure odd number for kernel
        if value % 2 == 0:
            value += 1
        self.lbl_blur.setText(f"Blur Kernel: {value}")
        self.worker.blur_kernel = value

    def update_image(self, raw_qt, warped_qt):
        self.raw_video_label.setPixmap(QPixmap.fromImage(raw_qt))
        self.warped_video_label.setPixmap(QPixmap.fromImage(warped_qt))

    def append_log(self, text):
        print(f"LOG: {text}")  # Print to stdout for debugging
        self.log_text.append(text)
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)

    def calibrate(self):
        self.worker.command_calibrate()

    def rotate(self):
        self.worker.command_rotate()

    def start_game(self):
        self.worker.command_start_game()

    def stop_game(self):
        self.worker.command_stop_game()

    def export_pgn(self):
        # Save PGN file locally
        filename = self.worker.chess_system.export_pgn()
        self.append_log(f"Game exported to: {filename}")
        
        # Upload to Lichess and open in browser
        try:
            pgn_string = self.worker.chess_system.get_pgn_string()
            
            # Import to Lichess via API
            self.append_log("Uploading to Lichess...")
            response = requests.post(
                'https://lichess.org/api/import',
                data={'pgn': pgn_string}
            )
            
            if response.status_code == 200:
                result = response.json()
                game_url = result.get('url', '')
                
                if game_url:
                    # Open in Lichess Analysis
                    analysis_url = game_url.replace('/lichess.org/', '/lichess.org/analysis/')
                    webbrowser.open(analysis_url)
                    self.append_log(f"Opened in Lichess Analysis: {analysis_url}")
                    speak("Game opened in Lichess")
                else:
                    self.append_log("Error: No URL returned from Lichess")
                    speak("Failed to open in Lichess")
            else:
                self.append_log(f"Lichess API Error: {response.status_code}")
                self.append_log(f"Response: {response.text}")
                speak("Failed to upload to Lichess")
                
        except requests.exceptions.RequestException as e:
            self.append_log(f"Network error: {e}")
            speak("Network error")
        except Exception as e:
            self.append_log(f"Error uploading to Lichess: {e}")
            speak("Upload error")
        
        speak("Game exported")

    def undo_move(self):
        self.worker.command_undo()

    def toggle_debug(self, state):
        self.worker.set_debug_mode(state == Qt.Checked)

    def toggle_noturn(self, state):
        self.worker.set_no_turn_mode(state == Qt.Checked)

    def closeEvent(self, event):
        self.worker.running = False
        self.worker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

import sys
import cv2
import numpy as np
from ultralytics import YOLO
import pyttsx3
import threading
import chess
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage

from PyQt5.QtGui import QPixmap, QImage

# --- CONFIGURATION ---
CONF_THRESHOLD = 0.4
CAMERA_ID = 0

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
        
        self.class_map = {
            0: 'b', 1: 'k', 2: 'n', 3: 'p', 4: 'q', 5: 'r',
            6: 'B', 7: 'K', 8: 'N', 9: 'P', 10: 'Q', 11: 'R'
        }

    # ... (sync_board and _get_board_occupancy remain same)
    def sync_board(self, visual_occupancy_grid, ai_results):
        log_msgs = []
        log_msgs.append("Syncing internal board to visual state...")
        
        ai_piece_map = {}
        for r in ai_results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cls = int(box.cls[0])
                foot_x = (x1 + x2) / 2
                foot_y = y2
                col = int((foot_x - 100) // 100)
                row = int((foot_y - 100) // 100)
                col = max(0, min(7, col))
                row = max(0, min(7, row))
                if cls in self.class_map:
                    ai_piece_map[(row, col)] = self.class_map[cls]

        self.board.clear() # Clear board first to avoid artifacts
        
        for r in range(8):
            for c in range(8):
                rank = 7 - r
                file = c
                square = chess.square(file, rank)
                is_visually_occupied = visual_occupancy_grid[r][c]
                
                if is_visually_occupied:
                    if (r, c) in ai_piece_map:
                        piece_char = ai_piece_map[(r, c)]
                        piece = chess.Piece.from_symbol(piece_char)
                        log_msgs.append(f"Adding detected {piece_char} at {chess.square_name(square)}")
                        self.board.set_piece_at(square, piece)
                    else:
                        # Fallback if occupied but no class
                        log_msgs.append(f"WARNING: Occupied at {chess.square_name(square)} but class unknown. Assuming White Pawn.")
                        self.board.set_piece_at(square, chess.Piece.from_symbol('P'))
        
        self.expected_occupancy = self._get_board_occupancy(self.board)
        self.last_occupancy_grid = visual_occupancy_grid
        log_msgs.append("Board Sync Complete.")
        return log_msgs

    def _get_board_occupancy(self, board):
        grid = [[False for _ in range(8)] for _ in range(8)]
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                row = 7 - rank
                col = file
                grid[row][col] = True
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
                    
                    # Pass no_turn_mode to infer_move or handle it here?
                    # Better to handle it here before validation or inside infer_move helper if needed.
                    # Actually, we need to know the move first.
                    
                    move = self._infer_move(expected, detected_occupancy_grid, logs, debug_mode)
                    
                    if move:
                        # Check No Turn Mode
                        if no_turn_mode and not debug_mode:
                            # If valid move for *some* color, force turn to that color
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
                                except:
                                    san = move.uci()
                                    self.board.push(move)
                                self.stable_start_time = current_time 
                                return san, logs
                            else:
                                # Illegal Move Detected (Inferred but not legal)
                                logs.append(f"Illegal Move Detected: {move.uci()}")
                                speak("Illegal Move")
                                # Reset timer to avoid spamming "Illegal Move"
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

        if len(sources) == 1 and len(targets) == 1:
            src = to_square(*sources[0])
            dst = to_square(*targets[0])
            move = chess.Move(src, dst)
            
            if debug_mode:
                return move # Return raw move, ignored rules

            if self.board.piece_at(src) and self.board.piece_at(src).piece_type == chess.PAWN:
                if chess.square_rank(dst) in [0, 7]:
                    move = chess.Move(src, dst, promotion=chess.QUEEN)
            
            # Return move even if illegal, so update() can check legality and warn
            return move
                
        elif len(sources) == 1 and len(targets) == 0:
            src = to_square(*sources[0])
            if debug_mode:
                logs.append("DEBUG: Capture detected (Source disappeared). Target unknown in Debug Mode.")
                return None

            # For capture, we need to be careful. If we return a move here, it must be a capture.
            # If it's illegal, we should still return it if possible so we can say "Illegal Move".
            # But finding *which* capture is hard if there are multiple.
            # Let's stick to legal captures for inference, or return the first candidate.
            candidates = [m for m in self.board.legal_moves if m.from_square == src and self.board.is_capture(m)]
            if len(candidates) == 1:
                return candidates[0]
            elif len(candidates) > 1:
                logs.append(f"Ambiguous capture from {chess.square_name(src)}")

        elif len(sources) == 2 and len(targets) == 2:
            for move in self.board.legal_moves:
                if self.board.is_castling(move):
                    self.board.push(move)
                    temp_occ = self._get_board_occupancy(self.board)
                    self.board.pop()
                    if temp_occ == visual_grid:
                        return move

        elif len(sources) == 2 and len(targets) == 1:
             for move in self.board.legal_moves:
                if self.board.is_en_passant(move):
                    self.board.push(move)
                    temp_occ = self._get_board_occupancy(self.board)
                    self.board.pop()
                    if temp_occ == visual_grid:
                        return move
        return None

# --- WORKER THREAD ---
class VisionWorker(QThread):
    frame_update = pyqtSignal(QImage, QImage) # Raw, Warped
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.state = "WAITING" # WAITING, SETUP, GAME
        self.calibration_matrix = None
        self.chess_system = OccupancyChessSystem()
        self.model = None
        self.cap = None
        self.debug_mode = False
        self.no_turn_mode = False

    def set_debug_mode(self, enabled):
        self.debug_mode = enabled
        self.log_message.emit(f"Debug Mode: {enabled}")

    def set_no_turn_mode(self, enabled):
        self.no_turn_mode = enabled
        self.log_message.emit(f"No Turn Mode: {enabled}")

    def _apply_calibration(self, corners):
        # Indices: TL, TR, BR, BL
        base_indices = [0, 6, 48, 42]
        # Rotate indices based on rotation_index (Right shift)
        # 0: [0, 6, 48, 42]
        # 1: [42, 0, 6, 48] (90 deg CW)
        # ...
        
        shifted_indices = base_indices[:]
        for _ in range(self.rotation_index):
            shifted_indices = [shifted_indices[-1]] + shifted_indices[:-1]
            
        src_pts = np.float32([corners[i] for i in shifted_indices])
        dst_pts = np.float32([[200, 200], [800, 200], [800, 800], [200, 800]])
        
        self.calibration_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        self.state = "SETUP"
        self.last_raw_corners = corners # Save for re-rotation

    def command_rotate(self):
        self.rotation_index = (self.rotation_index + 1) % 4
        deg = self.rotation_index * 90
        self.log_message.emit(f"Rotated Board {deg}°")
        
        # Re-calibrate if we have corners
        if self.last_raw_corners is not None:
            self._apply_calibration(self.last_raw_corners)

    def command_set_a1_at(self, nx, ny):
        if self.last_raw_corners is None:
            self.log_message.emit("Error: No calibration data. Calibrate first.")
            return
            
        # Find closest corner to (nx, ny)
        # corners are in original frame coords. We need frame size.
        if self.cap is None: return
        w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        click_x = nx * w
        click_y = ny * h
        
        # Corners: TL, TR, BR, BL (usually, but we want to find the one closest to click)
        # We have self.last_raw_corners (49 points). 
        # The 4 corners of the board are indices 0, 6, 48, 42.
        corner_indices = [0, 6, 48, 42]
        min_dist = float('inf')
        closest_idx = -1
        
        for idx in corner_indices:
            pt = self.last_raw_corners[idx][0]
            dist = (pt[0] - click_x)**2 + (pt[1] - click_y)**2
            if dist < min_dist:
                min_dist = dist
                closest_idx = idx
                
        self.log_message.emit(f"Closest corner index: {closest_idx}")
        
        # We want closest_idx to be A1 (Bottom-Left in chess coords).
        # In our warped view mapping:
        # dst_pts = [[200, 200], [800, 200], [800, 800], [200, 800]]
        # This maps to: TL(a8), TR(h8), BR(h1), BL(a1)
        # So we want the clicked corner to map to [200, 800] (BL).
        
        # We need to rotate `corner_indices` list so that `closest_idx` is at the end (index 3).
        # Current order in _apply_calibration: [0, 6, 48, 42] -> [TL, TR, BR, BL]
        
        # Let's find where closest_idx is in the base list
        base_indices = [0, 6, 48, 42]
        if closest_idx not in base_indices: return
        
        idx_in_base = base_indices.index(closest_idx)
        # We want this to move to position 3.
        # shift amount?
        # If it's at 0 (TL), we want it at 3 (BL). Shift -1 or +3.
        # If it's at 1 (TR), we want it at 3. Shift +2.
        # If it's at 2 (BR), we want it at 3. Shift +1.
        # If it's at 3 (BL), we want it at 3. Shift 0.
        
        # Rotation index (CW rotations):
        # 0 rot: [0, 6, 48, 42] -> BL is 42
        # 1 rot: [42, 0, 6, 48] -> BL is 48
        # 2 rot: [48, 42, 0, 6] -> BL is 6
        # 3 rot: [6, 48, 42, 0] -> BL is 0
        
        # So:
        # If closest is 42 -> rot 0
        # If closest is 48 -> rot 1
        # If closest is 6  -> rot 2
        # If closest is 0  -> rot 3
        
        target_rot = 0
        if closest_idx == 42: target_rot = 0
        elif closest_idx == 48: target_rot = 1
        elif closest_idx == 6: target_rot = 2
        elif closest_idx == 0: target_rot = 3
        
        self.rotation_index = target_rot
        self._apply_calibration(self.last_raw_corners)
        self.log_message.emit(f"A1 set to corner {closest_idx}. Rotation: {target_rot*90}°")

    def command_auto_orient(self):
        # Heuristic: Detect pieces. 
        # White pieces (Class 0-5 in my map? No, check class_map)
        # class_map = {0: 'b', 1: 'k', ... 6: 'B', 7: 'K' ...}
        # Lowercase = Black, Uppercase = White.
        # White IDs: 6, 7, 8, 9, 10, 11
        
        if self.last_results is None:
            self.log_message.emit("No detection results to orient from.")
            return

        # We need to look at the *current* warped view (which might be wrong)
        # and see where the white pieces are.
        # But wait, if we rotate, the warped view changes.
        # Let's just look at the current occupancy/classes in the current grid.
        
        # Count white pieces in top half vs bottom half
        white_top = 0
        white_bottom = 0
        
        # Grid is 8x8. Top is rows 0-3, Bottom is rows 4-7.
        # In our grid[row][col], row 0 is Top (Rank 8), row 7 is Bottom (Rank 1).
        # Standard chess: White is at Bottom (Rows 6,7).
        
        # We need to check the *classes* not just occupancy.
        # We need to re-run detection or store class info. 
        # sync_board does this. Let's peek at last_results.
        
        white_y_sum = 0
        white_count = 0
        
        for r in self.last_results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls >= 6: # White piece
                    # Box coords in warped image (1000x1000)
                    # y is 0 at top, 1000 at bottom.
                    _, y1, _, y2 = box.xyxy[0].tolist()
                    cy = (y1 + y2) / 2
                    white_y_sum += cy
                    white_count += 1
        
        if white_count == 0:
            self.log_message.emit("No white pieces found to orient.")
            return
            
        avg_y = white_y_sum / white_count
        
        # Center is 500.
        # If avg_y > 500, White is at Bottom -> Correct (0 deg or 180? No, 0 deg means A1 is BL).
        # Wait, if White is at Bottom, that's standard.
        # If White is at Top (avg_y < 500), we are upside down (180 deg).
        # What if White is Left or Right?
        # We also need X avg.
        
        white_x_sum = 0
        for r in self.last_results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls >= 6:
                    x1, _, x2, _ = box.xyxy[0].tolist()
                    cx = (x1 + x2) / 2
                    white_x_sum += cx
                    
        avg_x = white_x_sum / white_count
        
        # 0 deg: White at Bottom (y > 500)
        # 180 deg: White at Top (y < 500)
        # 90 deg CW: White at Left (x < 500) ? No, let's think.
        # If board is rotated 90 CW, A1 moves to TL. White (orig bottom) moves to Left.
        # So if White is Left -> 90 CW.
        # If White is Right -> 90 CCW (270 CW).
        
        # Logic:
        # Max deviation from center determines axis.
        dy = avg_y - 500
        dx = avg_x - 500
        
        if abs(dy) > abs(dx):
            # Vertical axis dominant
            if dy > 0: 
                # White at Bottom -> Correct (0 deg)
                self.log_message.emit("Auto-Orient: White is Bottom (0°)")
                target_rot = 0
            else:
                # White at Top -> 180 deg
                self.log_message.emit("Auto-Orient: White is Top (180°)")
                target_rot = 2 # 180
        else:
            # Horizontal axis dominant
            if dx < 0:
                # White at Left -> 90 CW
                self.log_message.emit("Auto-Orient: White is Left (90°)")
                target_rot = 1
            else:
                # White at Right -> 270 CW
                self.log_message.emit("Auto-Orient: White is Right (270°)")
                target_rot = 3
                
        # We need to apply this relative to current rotation?
        # No, this detects absolute position in *current* warped view.
        # If current view shows White at Top, we need to rotate 180 *more*?
        # Or does it mean we are currently 180 off?
        # Actually, we want White to be at Bottom.
        # If White is currently at Top, we need to add 180 to current rotation.
        # If White is Left, we need to add 90 (to bring Left to Bottom? No, Left is 90 CW from Bottom. So we need to rotate -90? or +270?)
        
        # Let's simplify:
        # We want the final image to have White at Bottom.
        # If currently White is at Top, we need to rotate 180.
        # If currently White is Left, we need to rotate 270 (CCW 90) to bring it to bottom.
        # If currently White is Right, we need to rotate 90 (CW 90) to bring it to bottom.
        
        offset = 0
        if abs(dy) > abs(dx):
            if dy > 0: offset = 0
            else: offset = 2
        else:
            if dx < 0: offset = 3 # Left -> Bottom needs 270 CW (or -90)
            else: offset = 1 # Right -> Bottom needs 90 CW
            
        self.rotation_index = (self.rotation_index + offset) % 4
        if self.last_raw_corners is not None:
            self._apply_calibration(self.last_raw_corners)

    def run(self):
        self.log_message.emit("Loading AI Model...")
        try:
            self.model = YOLO('/Users/yourside/Projects/chess-vision/ChessVision/chess_model.pt')
            # self.model = YOLO('/Users/yourside/Projects/chess-vision/runs/chess_detect/train3/weights/best.pt')
        except Exception as e:
            self.log_message.emit(f"Error loading model: {e}")
            return

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

            # Handle Calibration Request
            if self.request_calibration:
                corners = self.get_board_corners(frame)
                if corners is not None:
                    self._apply_calibration(corners)
                    self.log_message.emit("Calibrated Successfully.")
                    speak("Calibrated.")
                else:
                    self.log_message.emit("Calibration Failed: Board not found.")
                    speak("Board not found.")
                self.request_calibration = False

            # Process based on state
            if self.state == "WAITING":
                corners = self.get_board_corners(frame)
                if corners is not None:
                    cv2.drawChessboardCorners(frame, (7,7), corners, True)
                self.frame_update.emit(self.convert_cv_qt(frame), self.convert_cv_qt(np.zeros((300,300,3), np.uint8)))

            elif self.state in ["SETUP", "GAME"]:
                if self.calibration_matrix is not None:
                    warped = cv2.warpPerspective(frame, self.calibration_matrix, (1000, 1000))
                    results = self.model(warped, verbose=False, conf=CONF_THRESHOLD)
                    
                    occupancy_grid = [[False]*8 for _ in range(8)]
                    for r in results:
                        for box in r.boxes:
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            foot_x, foot_y = (x1 + x2) / 2, y2
                            col = int((foot_x - 100) // 100)
                            row = int((foot_y - 100) // 100)
                            col = max(0, min(7, col))
                            row = max(0, min(7, row))
                            occupancy_grid[row][col] = True
                    
                    annotated_warped = results[0].plot()
                    self.draw_grid_and_occupancy(annotated_warped, occupancy_grid)
                    
                    self.last_results = results
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

    # ... (helpers remain same)
    def calibrate(self):
        self.request_calibration = True # Simplified

    def get_board_corners(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (7,7), None)
        if ret: return corners
        return None

    def command_calibrate(self):
        self.request_calibration = True

    def command_start_game(self):
        self.state = "GAME"
        # Sync
        if hasattr(self, 'last_grid') and hasattr(self, 'last_results'):
            logs = self.chess_system.sync_board(self.last_grid, self.last_results)
            for log in logs:
                self.log_message.emit(log)
            speak("Game Started.")

    def command_stop_game(self):
        self.state = "SETUP"
        self.chess_system = OccupancyChessSystem() # FULL RESET
        speak("Game Stopped. System Reset.")

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return convert_to_Qt_format.scaled(400, 400, Qt.KeepAspectRatio)

    def draw_grid_and_occupancy(self, img, grid):
        cv2.rectangle(img, (100, 100), (900, 900), (0, 0, 255), 2)
        for i in range(1, 8):
            cv2.line(img, (100 + i*100, 100), (100 + i*100, 900), (0, 255, 0), 2)
            cv2.line(img, (100, 100 + i*100), (900, 100 + i*100), (0, 255, 0), 2)
            
        # Draw Labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        # Files a-h (columns 0-7)
        for c in range(8):
            x = int(100 + c * 100 + 35)
            y = 960 # Bottom margin
            cv2.putText(img, chr(ord('a') + c), (x, y), font, 1.5, (255, 255, 255), 3)
            
        # Ranks 1-8 (rows 7-0)
        for r in range(8):
            x = 40 # Left margin
            y = int(100 + r * 100 + 70)
            rank = 8 - r
            cv2.putText(img, str(rank), (x, y), font, 1.5, (255, 255, 255), 3)

        for r in range(8):
            for c in range(8):
                if grid[r][c]:
                    cx = int(100 + c * 100 + 50)
                    cy = int(100 + r * 100 + 50)
                    cv2.circle(img, (cx, cy), 15, (0, 255, 0), -1)

# --- GUI ---
class ClickableLabel(QLabel):
    clicked = pyqtSignal(int, int)
    def mousePressEvent(self, event):
        self.clicked.emit(event.x(), event.y())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlindChess Vision")
        self.setGeometry(100, 100, 1000, 800)

        # Layouts
        main_layout = QVBoxLayout()
        video_layout = QHBoxLayout()
        controls_layout = QHBoxLayout()

        # Video Widgets
        self.raw_video_label = ClickableLabel("Raw Video")
        self.warped_video_label = QLabel("Warped View")
        self.raw_video_label.setFixedSize(400, 400)
        self.warped_video_label.setFixedSize(400, 400)
        self.raw_video_label.setStyleSheet("background-color: black;")
        self.warped_video_label.setStyleSheet("background-color: black;")
        
        self.raw_video_label.clicked.connect(self.handle_video_click)
        
        video_layout.addWidget(self.raw_video_label)
        video_layout.addWidget(self.warped_video_label)

        # Log Widget
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace;")

        # Buttons
        self.btn_calibrate = QPushButton("Calibrate (Empty Board)")
        self.btn_rotate = QPushButton("Rotate 90°")
        self.btn_auto_orient = QPushButton("Auto-Orient (A1)")
        self.btn_start = QPushButton("Start Game")
        self.btn_stop = QPushButton("Stop Game")
        self.chk_debug = QCheckBox("Debug: Ignore Rules")
        self.chk_noturn = QCheckBox("No Turn Mode")
        
        self.btn_calibrate.clicked.connect(self.calibrate)
        self.btn_rotate.clicked.connect(self.rotate)
        self.btn_auto_orient.clicked.connect(self.auto_orient)
        self.btn_start.clicked.connect(self.start_game)
        self.btn_stop.clicked.connect(self.stop_game)
        self.chk_debug.stateChanged.connect(self.toggle_debug)
        self.chk_noturn.stateChanged.connect(self.toggle_noturn)
        
        controls_layout.addWidget(self.btn_calibrate)
        controls_layout.addWidget(self.btn_rotate)
        controls_layout.addWidget(self.btn_auto_orient)
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.chk_debug)
        controls_layout.addWidget(self.chk_noturn)

        # Assemble
        main_layout.addLayout(video_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.log_text)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Worker
        self.worker = VisionWorker()
        self.worker.frame_update.connect(self.update_image)
        self.worker.log_message.connect(self.append_log)
        self.worker.start()

    def update_image(self, raw_qt, warped_qt):
        self.raw_video_label.setPixmap(QPixmap.fromImage(raw_qt))
        self.warped_video_label.setPixmap(QPixmap.fromImage(warped_qt))

    def append_log(self, text):
        self.log_text.append(text)
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)

    def handle_video_click(self, x, y):
        # Map click to video coordinates (assuming 400x400 label matches video aspect or close enough)
        # Video is likely 640x480 or similar, but we scale to 400x400 for display.
        # We need to know the actual video size to map correctly, or the worker can handle normalized coords.
        # Let's send normalized coords (0.0-1.0)
        nx = x / 400.0
        ny = y / 400.0
        self.worker.command_set_a1_at(nx, ny)

    def calibrate(self):
        self.worker.command_calibrate()

    def rotate(self):
        self.worker.command_rotate()
        
    def auto_orient(self):
        self.worker.command_auto_orient()

    def start_game(self):
        self.worker.command_start_game()

    def stop_game(self):
        self.worker.command_stop_game()

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

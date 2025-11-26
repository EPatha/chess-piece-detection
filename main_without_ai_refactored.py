"""
BlindChess Vision - AI-Free Version (Refactored)
Uses edge-based occupancy detection instead of AI.
"""
import sys
import cv2
import numpy as np
import threading
import chess
import chess.pgn 
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QTextEdit, QCheckBox, QSlider, QGroupBox, QGridLayout)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image, ImageDraw, ImageFont

# Import from our new modules
from core.chess_logic import OccupancyChessSystem
from core.constants import EDGE_THRESHOLD, EDGE_DIFFERENCE_THRESHOLD, COLOR_LIGHT, COLOR_DARK
from utils.audio import speak 
from utils.text import expand_chess_text 
from gui.widgets import ClickableLabel

# Configuration
CAMERA_ID = 0

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
            if not ret:
                continue
            
            # Process calibration if requested
            if self.request_calibration:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                found, corners = cv2.findChessboardCorners(gray, (7, 7))
                if found:
                    self._apply_calibration(corners)
                    
                    # Capture empty board reference for edge-based detection
                    warped = cv2.warpPerspective(frame, self.calibration_matrix, (1000, 1000))
                    gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
                    blurred = cv2.GaussianBlur(gray_warped, (self.blur_kernel, self.blur_kernel), 0)
                    self.empty_board_reference = cv2.Canny(blurred, self.canny_low, self.canny_high)
                    # Apply morphology
                    kernel = np.ones((3, 3), np.uint8)
                    self.empty_board_reference = cv2.morphologyEx(self.empty_board_reference, cv2.MORPH_CLOSE, kernel)
                    
                    self.log_message.emit("Calibrated Successfully. Empty board reference captured.")
                    speak("Calibrated")
                else:
                    self.log_message.emit("Calibration Failed: Board not found.")
                self.request_calibration = False
            
            # Main processing loop
            if self.calibration_matrix is not None:
                warped = cv2.warpPerspective(frame, self.calibration_matrix, (1000, 1000))
                
                if self.state in ["SETUP", "GAME"]:
                    occupancy_grid = self.detect_occupancy_edge_based(warped)
                    
                    warped_display = warped.copy()
                    self.draw_grid_and_occupancy(warped_display, occupancy_grid, self.chess_system.last_move)
                    
                    if self.state == "GAME":
                        san, logs = self.chess_system.update(occupancy_grid, self.debug_mode, self.no_turn_mode)
                        for log in logs:
                            self.log_message.emit(log)
                        if san:
                            self.log_message.emit(f"MOVE: {san} -> {expand_chess_text(san)}")
                            speak(expand_chess_text(san))
                            board_str = str(self.chess_system.board)
                            for line in board_str.split('\n'):
                                self.log_message.emit(line)
            else:
                warped_display = np.zeros((1000, 1000, 3), dtype=np.uint8)
                cv2.putText(warped_display, "Please Calibrate", (300, 500), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            
            # Convert frames to Qt
            raw_qt = self.convert_cv_qt(frame)
            warped_qt = self.convert_cv_qt(warped_display)
            self.frame_update.emit(raw_qt, warped_qt)
            
            time.sleep(0.033)  # ~30 FPS
        
        if self.cap:
            self.cap.release()

    def command_calibrate(self):
        self.request_calibration = True
    
    def command_start_game(self):
        if self.calibration_matrix is None:
            self.log_message.emit("Please calibrate first!")
            return
        
        # Capture current occupancy
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and self.calibration_matrix is not None:
                warped = cv2.warpPerspective(frame, self.calibration_matrix, (1000, 1000))
                occupancy = self.detect_occupancy_edge_based(warped)
                logs = self.chess_system.sync_board(occupancy)
                for log in logs:
                    self.log_message.emit(log)
        
        self.state = "GAME"
        speak("Game Started")
        
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
        # Fill background
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
                
                # Draw Coordinates
                font_scale = 0.5
                font_color = COLOR_DARK if (r + c) % 2 == 0 else COLOR_LIGHT
                
                if c == 0:
                    rank_label = str(8 - r)
                    cv2.putText(img, rank_label, (x1 + 5, y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 1)
                    
                if r == 7:
                    file_label = chr(ord('a') + c)
                    cv2.putText(img, file_label, (x2 - 20, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 1)

        # Highlight last move
        if last_move:
            from_square = last_move.from_square
            to_square = last_move.to_square
            
            HIGHLIGHT_COLOR = (100, 255, 255) # Yellow
            
            for sq in [from_square, to_square]:
                f = chess.square_file(sq)
                r = 7 - chess.square_rank(sq)
                x1 = 100 + f * 100
                y1 = 100 + r * 100
                
                sub_img = img[y1:y1+100, x1:x1+100]
                colored_rect = np.zeros(sub_img.shape, dtype=np.uint8)
                colored_rect[:] = HIGHLIGHT_COLOR
                res = cv2.addWeighted(sub_img, 0.6, colored_rect, 0.4, 1.0)
                img[y1:y1+100, x1:x1+100] = res

        # Draw Pieces using PIL
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        try:
            font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
            font = ImageFont.truetype(font_path, 80)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", 80)
            except:
                font = ImageFont.load_default()

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
                rank = 7 - r
                file = c
                square = chess.square(file, rank)
                piece = self.chess_system.board.piece_at(square)
                
                cx = int(100 + c * 100 + 50)
                cy = int(100 + r * 100 + 50)

                if piece:
                    text = piece_map[piece.color].get(piece.piece_type, '?')
                    text_color = (255, 255, 255) if piece.color == chess.WHITE else (0, 0, 0)
                    
                    bbox = draw.textbbox((0, 0), text, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    tx = cx - w / 2
                    ty = cy - h / 2 - 10 
                    
                    draw.text((tx, ty), text, font=font, fill=text_color)
                
                if grid[r][c]:
                    dx = cx + 35
                    dy = cy + 35
                    draw.ellipse((dx-10, dy-10, dx+10, dy+10), fill=(0, 255, 0), outline=(0,0,0))

        # Draw Turn Indicator
        turn_text = "White's Turn" if self.chess_system.board.turn == chess.WHITE else "Black's Turn"
        turn_color = (255, 255, 255) if self.chess_system.board.turn == chess.WHITE else (255, 0, 0)
        try:
            font_small = ImageFont.truetype("Arial.ttf", 40)
        except:
            font_small = ImageFont.load_default()
        draw.text((50, 20), turn_text, font=font_small, fill=turn_color)

        img[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# --- GUI ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlindChess Vision (AI-Free, Refactored)")
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QHBoxLayout()
        video_layout = QHBoxLayout()
        controls_layout = QVBoxLayout()
        params_layout = QVBoxLayout()

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
        params_grid.setColumnStretch(1, 3)
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
        
        # Diff Threshold
        self.lbl_diff_thresh = QLabel(f"Diff Threshold: {EDGE_DIFFERENCE_THRESHOLD}")
        self.lbl_diff_thresh.setMinimumWidth(180)
        self.slider_diff_thresh = QSlider(Qt.Horizontal)
        self.slider_diff_thresh.setMinimum(10)
        self.slider_diff_thresh.setMaximum(500)
        self.slider_diff_thresh.setValue(EDGE_DIFFERENCE_THRESHOLD)
        self.slider_diff_thresh.setMinimumWidth(300)
        self.slider_diff_thresh.valueChanged.connect(self.update_diff_threshold)
        params_grid.addWidget(self.lbl_diff_thresh, 1, 0)
        params_grid.addWidget(self.slider_diff_thresh, 1, 1)
        
        # Canny Low
        self.lbl_canny_low = QLabel(f"Canny Low: 100")
        self.lbl_canny_low.setMinimumWidth(180)
        self.slider_canny_low = QSlider(Qt.Horizontal)
        self.slider_canny_low.setMinimum(10)
        self.slider_canny_low.setMaximum(300)
        self.slider_canny_low.setValue(100)
        self.slider_canny_low.setMinimumWidth(300)
        self.slider_canny_low.valueChanged.connect(self.update_canny_low)
        params_grid.addWidget(self.lbl_canny_low, 2, 0)
        params_grid.addWidget(self.slider_canny_low, 2, 1)
        
        # Canny High
        self.lbl_canny_high = QLabel(f"Canny High: 200")
        self.lbl_canny_high.setMinimumWidth(180)
        self.slider_canny_high = QSlider(Qt.Horizontal)
        self.slider_canny_high.setMinimum(50)
        self.slider_canny_high.setMaximum(500)
        self.slider_canny_high.setValue(200)
        self.slider_canny_high.setMinimumWidth(300)
        self.slider_canny_high.valueChanged.connect(self.update_canny_high)
        params_grid.addWidget(self.lbl_canny_high, 3, 0)
        params_grid.addWidget(self.slider_canny_high, 3, 1)
        
        # Blur Kernel
        self.lbl_blur = QLabel(f"Blur Kernel: 5")
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
        if value % 2 == 0:
            value += 1
        self.lbl_blur.setText(f"Blur Kernel: {value}")
        self.worker.blur_kernel = value

    def update_image(self, raw_qt, warped_qt):
        self.raw_video_label.setPixmap(QPixmap.fromImage(raw_qt))
        self.warped_video_label.setPixmap(QPixmap.fromImage(warped_qt))

    def append_log(self, text):
        print(f"LOG: {text}")
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
        filename = self.worker.chess_system.export_pgn()
        self.append_log(f"Game exported to: {filename}")
        speak(f"Game exported")

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

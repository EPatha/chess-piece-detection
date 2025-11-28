import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QGroupBox, QComboBox, QSlider, QCheckBox, QMessageBox, QScrollArea, QTabWidget, QSplitter)
from PyQt5.QtCore import Qt, pyqtSlot
from core.camera_thread import CameraThread
from core.processing_thread import ProcessingThread
from core.hybrid_manager import HybridManager
from core.config_manager import ConfigManager
from ui.panels.raw_camera_panel import RawCameraPanel
from ui.panels.cropped_camera_panel import CroppedCameraPanel
from ui.panels.board_view_panel import BoardViewPanel
from ui.panels.piece_status_panel import PieceStatusPanel
from ui.panels.history_panel import HistoryPanel
from ui.panels.log_view_panel import LogViewPanel
from ui.panels.evaluation_panel import EvaluationPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.setWindowTitle("ChessMind Hybrid Vision System")
        self.resize(1300, 850) # Compact size
        self.setStyleSheet(self.get_stylesheet())
        
        # Initialize Core Threads & Managers
        self.camera_thread = CameraThread()
        self.processing_thread = ProcessingThread()
        
        game_mode = self.config_manager.get("features.game_mode", True)
        print(f"MainWindow: Game Mode Enabled: {game_mode}")
        self.hybrid_manager = HybridManager(game_mode_enabled=game_mode)
        self.hybrid_manager.promotion_callback = self.ask_for_promotion
        
        # Initialize UI Panels
        self.raw_panel = RawCameraPanel()
        self.cropped_panel = CroppedCameraPanel()
        self.board_panel = BoardViewPanel()
        self.status_panel = PieceStatusPanel()
        self.history_panel = HistoryPanel()
        self.eval_panel = EvaluationPanel()
        self.log_panel = LogViewPanel()
        
        # Connect signals
        # Camera -> UI
        self.camera_thread.frame_ready.connect(self.raw_panel.update_frame)
        self.camera_thread.frame_ready.connect(self.processing_thread.update_frame)
        self.camera_thread.log_message.connect(self.log_panel.add_entry)
        
        # Processing -> UI
        self.processing_thread.processed_frame_ready.connect(self.cropped_panel.update_frame)
        self.processing_thread.debug_corners_detected.connect(self.raw_panel.set_debug_points)
        
        # Processing -> HybridManager
        self.processing_thread.board_state_updated.connect(self.hybrid_manager.update_board_state)
        
        # HybridManager -> UI
        self.hybrid_manager.game_state_updated.connect(self.board_panel.update_fen)
        self.hybrid_manager.game_state_updated.connect(lambda fen, move: self.status_panel.update_game_info(fen))
        self.hybrid_manager.game_state_updated.connect(lambda fen, move: self.history_panel.update_history(self.hybrid_manager.get_pgn()))
        self.hybrid_manager.evaluation_updated.connect(self.eval_panel.update_evaluation)
        self.hybrid_manager.best_move_found.connect(self.board_panel.set_best_move)
        self.hybrid_manager.log_message.connect(self.log_panel.add_entry)
        self.hybrid_manager.illegal_move_attempted.connect(self.handle_illegal_move)
        self.hybrid_manager.clock_updated.connect(self.status_panel.update_clock)
        self.processing_thread.log_message.connect(self.log_panel.add_entry)
        self.processing_thread.yolo_state_updated.connect(self.hybrid_manager.update_yolo_state)
        self.processing_thread.scan_completed.connect(self.on_scan_completed)
        
        # Start threads
        self.processing_thread.start()
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5) # Reduce global margins
        main_layout.setSpacing(5)
        
        # Main Splitter (Vertical)
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(5)
        
        # Top Section: Panels Container
        panels_widget = QWidget()
        panels_layout = QHBoxLayout(panels_widget)
        panels_layout.setContentsMargins(0, 0, 0, 0)
        panels_layout.setSpacing(5)
        
        # Left Column: Camera Views
        camera_layout = QVBoxLayout()
        camera_layout.addWidget(self.raw_panel)
        camera_layout.addWidget(self.cropped_panel)
        panels_layout.addLayout(camera_layout, 1)
        
        # Center Column: Board View & Status
        center_layout = QVBoxLayout()
        center_layout.setSpacing(5)
        
        # Feature: Clock Mode
        if self.config_manager.get("features.clock_mode", True):
            center_layout.addWidget(self.status_panel, 0) # Add Status Panel at top
        else:
            self.status_panel.hide() # Or just don't add it
            
        center_layout.addWidget(self.board_panel, 1)  # Board takes remaining space
        panels_layout.addLayout(center_layout, 4)     # Give center column MUCH more width (4 vs 1)
        
        # Right Column: Tabbed Info
        right_tabs = QTabWidget()
        right_tabs.addTab(self.history_panel, "History")
        
        # Feature: Game Mode (Engine)
        if self.config_manager.get("features.game_mode", True):
            right_tabs.addTab(self.eval_panel, "Analysis")
        else:
            self.eval_panel.hide()
            
        right_tabs.addTab(self.log_panel, "Logs")
        panels_layout.addWidget(right_tabs, 1)
        
        splitter.addWidget(panels_widget)
        
        # Bottom Section: Control Panel
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # Set initial sizes (approx 75% top, 25% bottom)
        splitter.setSizes([800, 200])
        
        main_layout.addWidget(splitter)

    def get_stylesheet(self):
        from ui.styles import STYLESHEET
        return STYLESHEET

    def create_control_panel(self):
        group_box = QGroupBox("Control Panel")
        group_layout = QVBoxLayout(group_box)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame) # Seamless look
        
        # Content Widget
        content_widget = QWidget()
        
        # Main Layout: 3 Columns
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # --- Column 1: Vision & Camera ---
        col1_layout = QVBoxLayout()
        col1_layout.setSpacing(5)
        
        # Header with Help
        header_layout = QHBoxLayout()
        header_lbl = QLabel("CAMERA & VISION")
        header_lbl.setStyleSheet("color: #888; font-size: 12px; font-weight: bold;")
        header_layout.addWidget(header_lbl)
        header_layout.addStretch()
        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(24, 24)
        self.help_btn.setObjectName("infoBtn")
        self.help_btn.setToolTip("Show Help")
        self.help_btn.clicked.connect(self.show_help)
        header_layout.addWidget(self.help_btn)
        col1_layout.addLayout(header_layout)
        
        # Camera Source
        cam_row = QHBoxLayout()
        cam_row.addWidget(QLabel("Source:"))
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Camera 0", "Camera 1"])
        cam_row.addWidget(self.camera_combo)
        col1_layout.addLayout(cam_row)
        
        # YOLO Model Selection (Phase 2)
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.refresh_models() # Populate models
        self.model_combo.currentIndexChanged.connect(self.load_selected_model)
        model_row.addWidget(self.model_combo)
        col1_layout.addLayout(model_row)

        self.yolo_check = QCheckBox("Enable YOLO")
        self.yolo_check.stateChanged.connect(lambda state: self.processing_thread.toggle_yolo(state == Qt.Checked))
        col1_layout.addWidget(self.yolo_check)
        
        self.yolo_check.stateChanged.connect(lambda state: self.processing_thread.toggle_yolo(state == Qt.Checked))
        col1_layout.addWidget(self.yolo_check)
        
        # Feature: Sync Edit
        if self.config_manager.get("features.sync_edit", True):
            # Sync Board Button (Phase 2)
            self.sync_btn = QPushButton("Sync Board from Camera")
            self.sync_btn.setToolTip("Initialize board state from current YOLO detections")
            self.sync_btn.clicked.connect(self.hybrid_manager.sync_board_from_camera)
            col1_layout.addWidget(self.sync_btn)

            self.auto_sync_check = QCheckBox("Auto-sync on Reset")
            self.auto_sync_check.setToolTip("Automatically sync board from camera when resetting game")
            self.auto_sync_check.stateChanged.connect(lambda state: setattr(self.hybrid_manager, 'auto_sync_on_reset', state == Qt.Checked))
            col1_layout.addWidget(self.auto_sync_check)
            
            # Scan & Edit Button
            self.scan_btn = QPushButton("Scan & Edit")
            self.scan_btn.setToolTip("Scan board for 1 second, then edit manually")
            def start_scan_with_audio():
                self.hybrid_manager.audio_manager.speak("Scanning")
                self.processing_thread.start_scan(30)
            self.scan_btn.clicked.connect(start_scan_with_audio)
            col1_layout.addWidget(self.scan_btn)
        
        # Camera Buttons
        cam_btn_row = QHBoxLayout()
        self.start_cam_btn = QPushButton("Start Camera")
        self.start_cam_btn.setObjectName("successBtn")
        self.stop_cam_btn = QPushButton("Stop")
        self.stop_cam_btn.setObjectName("dangerBtn")
        self.start_cam_btn.clicked.connect(self.start_camera)
        self.stop_cam_btn.clicked.connect(self.stop_camera)
        cam_btn_row.addWidget(self.start_cam_btn)
        cam_btn_row.addWidget(self.stop_cam_btn)
        col1_layout.addLayout(cam_btn_row)
        
        # Iriun Webcam Test Button
        self.test_iriun_btn = QPushButton("Test Iriun Webcam")
        self.test_iriun_btn.setObjectName("primaryBtn")
        self.test_iriun_btn.setToolTip("Scan and test Iriun webcam sources (indexes 0-10)")
        self.test_iriun_btn.clicked.connect(self.test_iriun_cameras)
        col1_layout.addWidget(self.test_iriun_btn)
        
        # Calibration Buttons
        self.auto_detect_btn = QPushButton("Auto Detect Board")
        self.auto_detect_btn.setObjectName("primaryBtn")
        self.auto_detect_btn.clicked.connect(self.toggle_auto_detect)
        col1_layout.addWidget(self.auto_detect_btn)
        
        self.cal_btn = QPushButton("Manual Calibration")
        self.cal_btn.clicked.connect(self.start_calibration)
        col1_layout.addWidget(self.cal_btn)
        
        # Connect Calibration Signals
        self.raw_panel.calibration_point_clicked.connect(self.on_calibration_click)
        self.processing_thread.board_detected.connect(self.on_board_detected)
        
        # Debug Checkbox
        self.raw_crop_chk = QCheckBox("Show Raw Crop (Color)")
        self.raw_crop_chk.toggled.connect(self.toggle_raw_crop)
        col1_layout.addWidget(self.raw_crop_chk)
        
        col1_layout.addStretch()
        main_layout.addLayout(col1_layout, 1)
        
        # Separator
        line1 = QWidget()
        line1.setFixedWidth(1)
        line1.setStyleSheet("background-color: #3e3e3e;")
        main_layout.addWidget(line1)
        
        # --- Column 2: Game Control ---
        col2_layout = QVBoxLayout()
        col2_layout.setSpacing(8) # Slightly increased spacing
        
        header_lbl2 = QLabel("GAME CONTROL")
        header_lbl2.setStyleSheet("color: #888; font-size: 12px; font-weight: bold;")
        header_lbl2.setAlignment(Qt.AlignCenter)
        col2_layout.addWidget(header_lbl2)
        
        # Mode Selection
        if self.config_manager.get("features.game_mode", True):
            mode_row = QHBoxLayout()
            mode_row.addStretch()
            mode_row.addWidget(QLabel("Mode:"))
            self.mode_combo = QComboBox()
            self.mode_combo.addItems(["Human vs Human", "Play as White", "Play as Black"])
            self.mode_combo.currentIndexChanged.connect(self.change_game_mode)
            mode_row.addWidget(self.mode_combo)
            mode_row.addStretch()
            col2_layout.addLayout(mode_row)
        
        # Flip Board
        self.flip_btn = QPushButton("Flip Board View")
        self.flip_btn.clicked.connect(self.board_panel.flip_board)
        col2_layout.addWidget(self.flip_btn, 0, Qt.AlignCenter)
        
        # Analysis Toggle
        if self.config_manager.get("features.game_mode", True):
            self.analysis_check = QCheckBox("Stockfish Analysis")
            self.analysis_check.stateChanged.connect(lambda state: self.hybrid_manager.toggle_analysis(state == Qt.Checked))
            col2_layout.addWidget(self.analysis_check, 0, Qt.AlignCenter)
        
        # Clock Mode Toggle
        self.clock_check = QCheckBox("Show Clock")
        self.clock_check.stateChanged.connect(lambda state: self.status_panel.toggle_clock(state == Qt.Checked))
        col2_layout.addWidget(self.clock_check, 0, Qt.AlignCenter)
        
        # Action Buttons
        actions_row = QHBoxLayout()
        actions_row.addStretch()
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.hybrid_manager.undo_last_move)
        actions_row.addWidget(self.undo_btn)
        
        self.reset_btn = QPushButton("Reset Game")
        self.reset_btn.setObjectName("dangerBtn")
        self.reset_btn.clicked.connect(self.confirm_reset)
        actions_row.addWidget(self.reset_btn)
        actions_row.addStretch()
        col2_layout.addLayout(actions_row)
        
        self.correction_btn = QPushButton("Manual Correction")
        self.correction_btn.setObjectName("warningBtn")
        self.correction_btn.clicked.connect(self.open_manual_correction)
        col2_layout.addWidget(self.correction_btn, 0, Qt.AlignCenter)
        
        # FEN Controls
        if self.config_manager.get("features.copy_paste_fen", True):
            fen_row = QHBoxLayout()
            fen_row.addStretch()
            self.copy_fen_btn = QPushButton("Copy FEN")
            self.paste_fen_btn = QPushButton("Paste FEN")
            self.copy_fen_btn.clicked.connect(self.copy_fen)
            self.paste_fen_btn.clicked.connect(self.paste_fen)
            fen_row.addWidget(self.copy_fen_btn)
            fen_row.addWidget(self.paste_fen_btn)
            fen_row.addStretch()
            col2_layout.addLayout(fen_row)
        
        # Export Buttons
        export_row = QHBoxLayout()
        export_row.addStretch()
        self.export_btn = QPushButton("PGN")
        self.export_btn.clicked.connect(self.export_pgn)
        export_row.addWidget(self.export_btn)
        
        self.lichess_btn = QPushButton("Lichess")
        self.lichess_btn.clicked.connect(self.export_to_lichess)
        export_row.addWidget(self.lichess_btn)
        export_row.addStretch()
        col2_layout.addLayout(export_row)
        
        col2_layout.addStretch()
        main_layout.addLayout(col2_layout, 1)
        
        # Separator
        line2 = QWidget()
        line2.setFixedWidth(1)
        line2.setStyleSheet("background-color: #3e3e3e;")
        main_layout.addWidget(line2)
        
        # --- Column 3: Fine Tuning ---
        col3_layout = QVBoxLayout()
        col3_layout.setSpacing(5)
        
        header_lbl3 = QLabel("FINE TUNING")
        header_lbl3.setStyleSheet("color: #888; font-size: 12px; font-weight: bold;")
        col3_layout.addWidget(header_lbl3)
        
        # Edge Detection
        col3_layout.addWidget(QLabel("Edge Detection (Canny):"))
        canny_row = QHBoxLayout()
        
        # Lower
        l_layout = QVBoxLayout()
        l_layout.addWidget(QLabel("Lower"))
        self.canny_lower_slider = QSlider(Qt.Horizontal)
        self.canny_lower_slider.setRange(0, 255)
        self.canny_lower_slider.setValue(50)
        self.canny_lower_slider.valueChanged.connect(self.update_processing_params)
        l_layout.addWidget(self.canny_lower_slider)
        canny_row.addLayout(l_layout)
        
        # Upper
        u_layout = QVBoxLayout()
        u_layout.addWidget(QLabel("Upper"))
        self.canny_upper_slider = QSlider(Qt.Horizontal)
        self.canny_upper_slider.setRange(0, 255)
        self.canny_upper_slider.setValue(150)
        self.canny_upper_slider.valueChanged.connect(self.update_processing_params)
        u_layout.addWidget(self.canny_upper_slider)
        canny_row.addLayout(u_layout)
        
        col3_layout.addLayout(canny_row)
        
        # Robustness
        col3_layout.addWidget(QLabel("Robustness:"))
        
        # Occupancy
        col3_layout.addWidget(QLabel("Occupancy Threshold"))
        self.occupancy_slider = QSlider(Qt.Horizontal)
        self.occupancy_slider.setRange(10, 200)
        self.occupancy_slider.setValue(50)
        self.occupancy_slider.valueChanged.connect(self.update_robustness_params)
        col3_layout.addWidget(self.occupancy_slider)
        
        # Stability
        col3_layout.addWidget(QLabel("Stability (Frames)"))
        self.stability_slider = QSlider(Qt.Horizontal)
        self.stability_slider.setRange(1, 30)
        self.stability_slider.setValue(5)
        self.stability_slider.valueChanged.connect(self.update_robustness_params)
        col3_layout.addWidget(self.stability_slider)
        
        col3_layout.addStretch()
        main_layout.addLayout(col3_layout, 1)
        
        # Set scroll widget
        scroll.setWidget(content_widget)
        group_layout.addWidget(scroll)
        
        return group_box

    def start_camera(self):
        if not self.camera_thread.isRunning():
            # Update camera ID from combo box
            idx = self.camera_combo.currentIndex()
            self.camera_thread.camera_id = idx
            self.camera_thread.start()
            self.log_panel.add_entry("info", f"Starting camera {idx}...")
            self.start_cam_btn.setEnabled(False)
            self.stop_cam_btn.setEnabled(True)

    def stop_camera(self):
        if self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.log_panel.add_entry("info", "Stopping camera...")
            self.start_cam_btn.setEnabled(True)
            self.stop_cam_btn.setEnabled(False)

    def test_iriun_cameras(self):
        """Test multiple camera indexes to find Iriun webcam"""
        import cv2
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout
        
        self.log_panel.add_entry("info", "Scanning for available cameras (0-10)...")
        
        available_cameras = []
        
        # Test camera indexes 0-10
        for i in range(11):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # Get camera resolution
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    available_cameras.append((i, f"Camera {i} - {width}x{height}"))
                    self.log_panel.add_entry("success", f"Found: Camera {i} ({width}x{height})")
                cap.release()
        
        if not available_cameras:
            self.log_panel.add_entry("error", "No cameras found!")
            return
        
        # Create selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Iriun Webcam")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Available cameras detected:"))
        
        camera_list = QListWidget()
        for idx, name in available_cameras:
            camera_list.addItem(name)
        layout.addWidget(camera_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        def select_and_start():
            selected_idx = camera_list.currentRow()
            if selected_idx >= 0:
                camera_id = available_cameras[selected_idx][0]
                self.log_panel.add_entry("info", f"Selected Camera {camera_id}")
                
                # Stop current camera if running
                if self.camera_thread.isRunning():
                    self.camera_thread.stop()
                
                # Update camera ID and start
                self.camera_thread.camera_id = camera_id
                self.camera_combo.setCurrentIndex(camera_id)
                self.camera_thread.start()
                
                self.log_panel.add_entry("success", f"Started Camera {camera_id} - Check Raw Camera View")
                self.start_cam_btn.setEnabled(False)
                self.stop_cam_btn.setEnabled(True)
                
                dialog.accept()
        
        select_btn = QPushButton("Select && Start")
        select_btn.setObjectName("successBtn")
        select_btn.clicked.connect(select_and_start)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()

    def start_calibration(self):
        self.log_panel.add_entry("info", "Calibration started. Click 4 corners: TL -> TR -> BR -> BL")
        self.raw_panel.set_calibration_mode(True)
        self.calibration_points = []
        self.cal_btn.setEnabled(False)
        self.cal_btn.setText("Calibrating...")

    def on_calibration_click(self, x, y):
        self.calibration_points.append((x, y))
        count = len(self.calibration_points)
        self.log_panel.add_entry("info", f"Captured point {count}/4 at ({x}, {y})")
        
        if count == 4:
            self.finish_calibration()

    def finish_calibration(self):
        self.raw_panel.set_calibration_mode(False)
        self.cal_btn.setEnabled(True)
        self.cal_btn.setText("Manual Calibration")
        
        if len(self.calibration_points) == 4:
            self.processing_thread.set_calibration_points(self.calibration_points)
            self.log_panel.add_entry("success", "Calibration complete! Homography applied.")
        else:
            self.log_panel.add_entry("error", "Calibration failed: Need exactly 4 points.")

    def toggle_auto_detect(self):
        if not self.processing_thread.is_auto_detecting:
            self.processing_thread.start_auto_detect()
            self.auto_detect_btn.setText("Scanning... (Stop)")
            self.auto_detect_btn.setObjectName("warningBtn")
            self.auto_detect_btn.setStyleSheet("") # Force refresh
            self.log_panel.add_entry("info", "Auto-detection started. Please ensure board is EMPTY.")
        else:
            self.processing_thread.stop_auto_detect()
            self.auto_detect_btn.setText("Auto Detect Board")
            self.auto_detect_btn.setObjectName("primaryBtn")
            self.auto_detect_btn.setStyleSheet("") # Force refresh
            self.log_panel.add_entry("info", "Auto-detection stopped.")

    def get_button_style(self):
        # Deprecated, using stylesheet
        return ""

    def on_board_detected(self, points):
        self.log_panel.add_entry("success", f"Board detected at: {points}")
        self.calibration_points = points
        self.raw_panel.set_detected_points(points)
        self.finish_calibration()
        
        # Reset button
        self.auto_detect_btn.setText("Auto Detect Board")
        self.auto_detect_btn.setObjectName("primaryBtn")
        self.auto_detect_btn.setStyleSheet("") # Force refresh

    def update_processing_params(self):
        lower = self.canny_lower_slider.value()
        upper = self.canny_upper_slider.value()
        self.processing_thread.update_params(lower, upper)

    def update_robustness_params(self):
        occupancy = self.occupancy_slider.value()
        stability = self.stability_slider.value()
        
        self.processing_thread.update_occupancy_threshold(occupancy)
        self.hybrid_manager.update_stability_threshold(stability)

    def toggle_raw_crop(self, checked):
        self.processing_thread.set_show_raw(checked)
        
    def reset_game(self):
        self.hybrid_manager.reset_game()
        
    def export_pgn(self):
        pgn = self.hybrid_manager.get_pgn()
        print(pgn)
        
        from PyQt5.QtWidgets import QFileDialog
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save PGN Game", "", "PGN Files (*.pgn);;All Files (*)", options=options)
        if fileName:
            try:
                with open(fileName, 'w') as f:
                    f.write(pgn)
                self.log_panel.add_entry("success", f"PGN saved to {fileName}")
            except Exception as e:
                self.log_panel.add_entry("error", f"Failed to save PGN: {e}")
        else:
            self.log_panel.add_entry("info", "PGN Export cancelled.")

    def ask_for_promotion(self):
        from PyQt5.QtWidgets import QInputDialog
        items = ["Queen", "Rook", "Bishop", "Knight"]
        item, ok = QInputDialog.getItem(self, "Pawn Promotion", 
                                        "Choose promotion piece:", items, 0, False)
        if ok and item:
            mapping = {"Queen": "q", "Rook": "r", "Bishop": "b", "Knight": "n"}
            return mapping.get(item, "q")
        return "q" # Default to Queen if cancelled

    def change_game_mode(self, index):
        modes = ["PvP", "PvAI_W", "PvAI_B"]
        if 0 <= index < len(modes):
            self.hybrid_manager.set_ai_mode(modes[index])
            
            # Auto-check engine box if AI mode
            if index > 0:
                self.analysis_check.setChecked(True)

    def confirm_reset(self):
        reply = QMessageBox.question(self, 'Reset Game', 
                                     "Are you sure you want to reset the game? All progress will be lost.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.hybrid_manager.reset_game()

    def open_manual_correction(self):
        from ui.dialogs.manual_correction_dialog import ManualCorrectionDialog
        current_fen = self.hybrid_manager.state_manager.get_fen()
        dialog = ManualCorrectionDialog(current_fen, self)
        if dialog.exec_():
            new_fen = dialog.get_fen()
            self.hybrid_manager.apply_manual_correction(new_fen)

    def copy_fen(self):
        import pyperclip
        fen = self.hybrid_manager.state_manager.get_fen()
        pyperclip.copy(fen)
        self.hybrid_manager.log_message.emit("info", "FEN copied to clipboard.")

    def paste_fen(self):
        import pyperclip
        import chess.pgn
        import io
        from PyQt5.QtWidgets import QMessageBox
        
        content = pyperclip.paste()
        fen_to_load = None
        source_type = "FEN"

        # Try parsing as PGN first
        try:
            pgn_io = io.StringIO(content)
            game = chess.pgn.read_game(pgn_io)
            if game and game.errors == []:
                # It's a valid PGN
                fen_to_load = game.end().board().fen()
                source_type = "PGN"
        except Exception:
            pass # Not a PGN or error parsing

        # If not PGN, treat as raw FEN
        if not fen_to_load:
            # Basic validation for FEN
            if len(content.split()) >= 4:
                fen_to_load = content
            else:
                self.hybrid_manager.log_message.emit("error", "Clipboard does not contain valid FEN or PGN.")
                return

        reply = QMessageBox.question(self, f'Paste {source_type}', 
                                     f"Load this position from {source_type}?\n{fen_to_load}",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.hybrid_manager.apply_manual_correction(fen_to_load)
            except Exception as e:
                self.hybrid_manager.log_message.emit("error", f"Invalid FEN: {e}")

    def show_help(self):
        from ui.dialogs.help_dialog import HelpDialog
        dialog = HelpDialog(self)
        dialog.exec_()

    def handle_illegal_move(self, move_uci):
        from ui.dialogs.desync_dialog import DesyncDialog
        dialog = DesyncDialog(move_uci, self)
        if dialog.exec_():
            action = dialog.result_action
            if action == "undo":
                self.hybrid_manager.undo_last_move()
            elif action == "manual":
                self.open_manual_correction()
            # if ignore, do nothing

    def export_to_lichess(self):
        from utils.lichess_exporter import LichessExporter
        import threading
        
        pgn = self.hybrid_manager.get_pgn()
        self.hybrid_manager.log_message.emit("info", "Exporting to Lichess...")
        
        def upload_task():
            try:
                url = LichessExporter.upload_pgn(pgn)
                if url:
                    self.hybrid_manager.log_message.emit("success", f"Uploaded to Lichess: {url}")
                else:
                    self.hybrid_manager.log_message.emit("error", "Failed to upload to Lichess.")
            except Exception as e:
                self.hybrid_manager.log_message.emit("error", f"Lichess Export Error: {e}")

        thread = threading.Thread(target=upload_task)
        thread.daemon = True
        thread.start()

    def keyPressEvent(self, event):
        # Keyboard Shortcuts
        if event.key() == Qt.Key_U:
            self.hybrid_manager.undo_last_move()
        elif event.key() == Qt.Key_R:
            self.confirm_reset()
        elif event.key() == Qt.Key_M:
            self.open_manual_correction()
        else:
            super().keyPressEvent(event)

    def refresh_models(self):
        self.model_combo.clear()
        self.model_combo.addItem("Select Model...")
        
        # Check current dir then parent dir
        paths_to_check = [
            os.path.join(os.getcwd(), "models"),
            os.path.join(os.getcwd(), "..", "models")
        ]
        
        models_dir = None
        for path in paths_to_check:
            if os.path.exists(path):
                models_dir = path
                break
        
        if models_dir:
            self.log_panel.add_entry("info", f"Found models in {models_dir}")
            for file in os.listdir(models_dir):
                if file.endswith(".pt"):
                    self.model_combo.addItem(file)
        else:
            self.log_panel.add_entry("warning", "No 'models' directory found.")

    def load_selected_model(self, index):
        if index <= 0: return # Skip "Select Model..."
        
        model_name = self.model_combo.currentText()
        
        # Find path again
        paths_to_check = [
            os.path.join(os.getcwd(), "models"),
            os.path.join(os.getcwd(), "..", "models")
        ]
        
        model_path = None
        for path in paths_to_check:
            p = os.path.join(path, model_name)
            if os.path.exists(p):
                model_path = p
                break
        
        if model_path:
            self.log_panel.add_entry("info", f"Loading model: {model_name}...")
            self.processing_thread.load_yolo_model(model_path)
            self.yolo_check.setChecked(True)
        else:
            self.log_panel.add_entry("error", f"Model file not found: {model_name}")

    def on_scan_completed(self, grid):
        self.log_panel.add_entry("success", "Scan complete. Opening editor...")
        self.hybrid_manager.audio_manager.speak("Scan complete")
        
        import chess
        board = chess.Board(None)
        board.clear()
        
        piece_map = {
            'white-pawn': chess.PAWN, 'white-rook': chess.ROOK, 'white-knight': chess.KNIGHT,
            'white-bishop': chess.BISHOP, 'white-queen': chess.QUEEN, 'white-king': chess.KING,
            'black-pawn': chess.PAWN, 'black-rook': chess.ROOK, 'black-knight': chess.KNIGHT,
            'black-bishop': chess.BISHOP, 'black-queen': chess.QUEEN, 'black-king': chess.KING
        }
        
        
        unknown_squares = []
        for row in range(8):
            for col in range(8):
                yolo_class = grid[row][col]
                if yolo_class == "unknown":
                    unknown_squares.append(chess.square(col, 7 - row))
                elif yolo_class and yolo_class != "empty":
                    piece_type = piece_map.get(yolo_class)
                    if piece_type:
                        color = chess.WHITE if 'white' in yolo_class else chess.BLACK
                        sq = chess.square(col, 7 - row)
                        board.set_piece_at(sq, chess.Piece(piece_type, color))
        
        board.turn = self.hybrid_manager.state_manager.board.turn # Keep current turn
        scanned_fen = board.fen()
        
        # Open Dialog
        from ui.dialogs.manual_correction_dialog import ManualCorrectionDialog
        dialog = ManualCorrectionDialog(scanned_fen, self, unknown_squares=unknown_squares)
        if dialog.exec_():
            new_fen = dialog.get_fen()
            self.hybrid_manager.apply_manual_correction(new_fen)

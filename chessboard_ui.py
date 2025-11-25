#!/usr/bin/env python3
"""
YOLOv8 Chessboard Grid Detection UI - USB Camera
Real-time detection of 64 chessboard squares
"""
import sys
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from ultralytics import YOLO
import threading
import time


class Worker(QtCore.QObject):
    """Background worker for camera capture and YOLO inference"""
    frame_ready = QtCore.pyqtSignal(object)
    finished = QtCore.pyqtSignal()
    status = QtCore.pyqtSignal(str)

    def __init__(self, camera_id=0, model_path=None, conf_threshold=0.25):
        super().__init__()
        self.camera_id = camera_id
        self._stop = threading.Event()
        self.conf_threshold = conf_threshold
        
        # Load YOLO model
        if model_path:
            self.model = YOLO(model_path)
        else:
            self.model = YOLO("runs/chessboard_detect/chessboard_grid8/weights/best.pt")
        
        self.status.emit(f"Model loaded: {len(self.model.names)} classes")

    def run(self):
        """Main loop for camera capture and inference"""
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            self.status.emit(f"❌ Failed to open camera {self.camera_id}")
            self.finished.emit()
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.status.emit(f"✅ Camera {self.camera_id} opened")
        
        while not self._stop.is_set():
            ret, frame = cap.read()
            
            if not ret:
                self.status.emit("❌ Failed to read frame")
                break
            
            # Run YOLO inference
            results = self.model(frame, conf=self.conf_threshold, verbose=False)
            
            # Draw results on frame
            annotated_frame = results[0].plot()
            
            # Count detections per class
            boxes = results[0].boxes
            class_counts = {}
            for box in boxes:
                cls = int(box.cls[0])
                class_name = self.model.names[cls]
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            # Add detection info to frame
            y_offset = 30
            for class_name, count in class_counts.items():
                text = f"{class_name}: {count}"
                cv2.putText(annotated_frame, text, (10, y_offset),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_offset += 30
            
            # Emit frame
            self.frame_ready.emit(annotated_frame)
        
        cap.release()
        self.finished.emit()

    def stop(self):
        """Stop the worker"""
        self._stop.set()


class ChessboardDetectionGUI(QtWidgets.QMainWindow):
    """Main GUI for chessboard grid detection"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chessboard Grid Detection - USB Camera")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        
        # Control panel
        control_layout = QtWidgets.QHBoxLayout()
        
        # Camera ID
        control_layout.addWidget(QtWidgets.QLabel("Camera ID:"))
        self.camera_id = QtWidgets.QSpinBox()
        self.camera_id.setRange(0, 10)
        self.camera_id.setValue(0)
        control_layout.addWidget(self.camera_id)
        
        # Confidence threshold
        control_layout.addWidget(QtWidgets.QLabel("Confidence:"))
        self.conf_threshold = QtWidgets.QDoubleSpinBox()
        self.conf_threshold.setRange(0.05, 0.95)
        self.conf_threshold.setValue(0.25)
        self.conf_threshold.setSingleStep(0.05)
        control_layout.addWidget(self.conf_threshold)
        
        # Model path
        control_layout.addWidget(QtWidgets.QLabel("Model:"))
        self.model_path = QtWidgets.QLineEdit()
        self.model_path.setText("runs/chessboard_detect/chessboard_grid8/weights/best.pt")
        control_layout.addWidget(self.model_path)
        
        # Start/Stop buttons
        self.start_btn = QtWidgets.QPushButton("Start Detection")
        self.start_btn.clicked.connect(self.start)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # Video display
        self.video_label = QtWidgets.QLabel()
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid black;")
        layout.addWidget(self.video_label)
        
        # Status bar
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")
        
        # Worker thread
        self.thread = None
        self.worker = None

    def start(self):
        """Start camera capture and detection"""
        cam_id = self.camera_id.value()
        conf = self.conf_threshold.value()
        model = self.model_path.text()
        
        # Create worker thread
        self.thread = QtCore.QThread()
        self.worker = Worker(cam_id, model, conf)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.frame_ready.connect(self.update_frame)
        self.worker.status.connect(self.status.showMessage)
        
        # Start thread
        self.thread.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status.showMessage("🔴 Detecting...")

    def stop(self):
        """Stop camera capture"""
        if self.worker:
            self.worker.stop()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status.showMessage("⏸ Stopped")

    def update_frame(self, frame):
        """Update video display with new frame"""
        # Convert frame to Qt format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        
        # Scale to fit label
        scaled = qt_image.scaled(
            self.video_label.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        
        self.video_label.setPixmap(QtGui.QPixmap.fromImage(scaled))


def main():
    """Entry point"""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = ChessboardDetectionGUI()
    
    # Set camera ID from command line if provided
    if len(sys.argv) > 1:
        try:
            cam_id = int(sys.argv[1])
            window.camera_id.setValue(cam_id)
            print(f"📷 Camera ID set to: {cam_id}")
        except ValueError:
            print(f"⚠️  Invalid camera ID: {sys.argv[1]}")
    
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

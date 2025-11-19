#!/usr/bin/env python3
"""
YOLOv8 PyQt5 USB Camera Viewer (Optimized for minimal delay)
- Direct USB camera capture only (no MJPEG streaming)
- Optimized for real-time performance with threading
- Same UI structure as yolov_ui.py
"""
import sys
import time
import threading
from typing import Optional

import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


class CaptureResult:
    """Container for frame data with timestamp"""
    def __init__(self, frame: np.ndarray, ts: float):
        self.frame = frame
        self.ts = ts


class Worker(QtCore.QObject):
    """Background thread worker for camera capture and YOLO inference"""
    frame_ready = QtCore.pyqtSignal(object)  # emits CaptureResult
    finished = QtCore.pyqtSignal()
    status = QtCore.pyqtSignal(str)

    def __init__(
        self,
        camera_id: int,
        model_path: Optional[str] = None,
        device: str = "cpu",
        fps: int = 30,
        conf_threshold: float = 0.15,
    ):
        super().__init__()
        self.camera_id = camera_id
        self.device = device
        self.fps = max(1, int(fps))
        self._stop = threading.Event()
        self.conf_threshold = conf_threshold

        # Load YOLO model
        self.model = None
        if YOLO and model_path:
            try:
                self.model = YOLO(model_path)
                self.status.emit(f"✅ YOLO model loaded: {model_path}")
            except Exception as e:
                self.status.emit(f"❌ Failed to load model: {e}")
                print(f"[ERROR] YOLO model loading failed: {e}")

    def stop(self):
        """Signal the worker to stop"""
        self._stop.set()

    def _infer(self, frame: np.ndarray) -> np.ndarray:
        """Run YOLO inference on frame"""
        if not self.model:
            return frame
        
        try:
            # Run inference with configured confidence threshold
            res = self.model(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                conf=self.conf_threshold,
                verbose=False
            )
            
            # Get annotated frame with bounding boxes
            try:
                annotated = res[0].plot()
                if isinstance(annotated, np.ndarray):
                    return annotated
            except Exception as e:
                print(f"[WARN] Annotation failed: {e}")
            
            return frame
        except Exception as e:
            print(f"[ERROR] Inference failed: {e}")
            return frame

    def run(self):
        """Main capture loop"""
        # Open USB camera
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            self.status.emit(f"❌ Failed to open camera {self.camera_id}")
            self.finished.emit()
            return

        # Optimize camera settings for minimal delay
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce latency
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # Get camera properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        
        self.status.emit(f"📹 Camera opened: {width}x{height} @ {actual_fps} FPS")
        
        # Calculate frame interval
        interval = 1.0 / self.fps
        last_time = time.time()
        frame_count = 0
        
        while not self._stop.is_set():
            # Read frame
            ret, frame = cap.read()
            
            if not ret or frame is None:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            
            # Run YOLO inference
            frame = self._infer(frame)
            
            # Emit frame to UI
            self.frame_ready.emit(CaptureResult(frame, time.time()))
            
            # FPS control
            elapsed = time.time() - last_time
            sleep_time = interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_time = time.time()
        
        # Cleanup
        cap.release()
        self.status.emit(f"📊 Capture stopped. Total frames: {frame_count}")
        self.finished.emit()


class YOLOGui(QtWidgets.QWidget):
    """Main GUI window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLOv8 USB Camera Viewer")
        self.resize(900, 700)

        # ==================== Input Controls ====================
        
        # Camera selection
        self.camera_id = QtWidgets.QSpinBox()
        self.camera_id.setRange(0, 10)
        self.camera_id.setValue(0)
        self.camera_id.setToolTip("USB camera index (0 = first camera, 1 = second, etc.)")
        
        # Model path
        self.model = QtWidgets.QLineEdit("runs/chess_detect/train3/weights/best.pt")
        self.model.setPlaceholderText("Path to YOLO model weights")
        
        # Device selection
        self.device = QtWidgets.QComboBox()
        self.device.addItems(["cpu", "mps", "cuda"])
        self.device.setCurrentText("mps")  # Default to Apple Silicon GPU
        
        # FPS control
        self.fps = QtWidgets.QSpinBox()
        self.fps.setRange(1, 60)
        self.fps.setValue(30)
        self.fps.setToolTip("Target frames per second")
        
        # Confidence threshold control
        self.conf_threshold = QtWidgets.QDoubleSpinBox()
        self.conf_threshold.setRange(0.05, 0.95)
        self.conf_threshold.setSingleStep(0.05)
        self.conf_threshold.setValue(0.15)
        self.conf_threshold.setDecimals(2)
        self.conf_threshold.setToolTip("Detection confidence threshold (0.10-0.20 recommended for chess)")
        
        # Control buttons
        self.start_btn = QtWidgets.QPushButton("▶ Start")
        self.stop_btn = QtWidgets.QPushButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        
        # ==================== Layout ====================
        
        # Form layout for controls
        form = QtWidgets.QFormLayout()
        form.addRow("📷 Camera ID:", self.camera_id)
        form.addRow("🤖 Model:", self.model)
        form.addRow("⚙️ Device:", self.device)
        form.addRow("🎬 FPS:", self.fps)
        form.addRow("🎯 Confidence:", self.conf_threshold)
        
        # Button layout
        control_layout = QtWidgets.QHBoxLayout()
        control_layout.addLayout(form)
        
        btns = QtWidgets.QVBoxLayout()
        btns.addWidget(self.start_btn)
        btns.addWidget(self.stop_btn)
        btns.addStretch()
        control_layout.addLayout(btns)
        
        # ==================== Video Preview ====================
        
        self.preview = QtWidgets.QLabel()
        self.preview.setFixedSize(860, 480)
        self.preview.setStyleSheet("background: black; border: 2px solid #333;")
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setText("📹 Camera preview will appear here")
        
        # ==================== Status Bar ====================
        
        self.status = QtWidgets.QStatusBar()
        self.status.showMessage("Ready. Click 'Start' to begin capture.")
        
        # ==================== Main Layout ====================
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(control_layout)
        layout.addWidget(self.preview)
        layout.addWidget(self.status)
        
        # ==================== Thread Management ====================
        
        self.thread = None
        self.worker = None
        
        # Connect signals
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)

    def _on_frame(self, capres: CaptureResult):
        """Update preview with new frame"""
        frame = capres.frame
        if frame is None:
            return
        
        # Convert to QImage
        h, w = frame.shape[:2]
        qimg = QtGui.QImage(
            frame.data,
            w,
            h,
            frame.strides[0],
            QtGui.QImage.Format_BGR888
        )
        
        # Scale and display
        pix = QtGui.QPixmap.fromImage(qimg).scaled(
            self.preview.width(),
            self.preview.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        self.preview.setPixmap(pix)

    def start(self):
        """Start camera capture and inference"""
        cam_id = int(self.camera_id.value())
        model_path = self.model.text().strip() or None
        device = self.device.currentText()
        fps = int(self.fps.value())
        conf = float(self.conf_threshold.value())
        
        # Create worker thread
        self.thread = QtCore.QThread()
        self.worker = Worker(
            camera_id=cam_id,
            model_path=model_path,
            device=device,
            fps=fps,
            conf_threshold=conf
        )
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.status.connect(self.status.showMessage)
        self.worker.frame_ready.connect(self._on_frame)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start capture
        self.thread.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status.showMessage("🔴 Capturing...")

    def stop(self):
        """Stop camera capture"""
        if self.worker:
            self.worker.stop()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status.showMessage("⏸ Capture stopped")


def main():
    """Entry point"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = YOLOGui()
    
    # Set camera ID from command line argument if provided
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

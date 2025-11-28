from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import cv2

class CameraThread(QThread):
    """
    Handles video capture from the webcam in a separate thread.
    Emits frames via signals to avoid blocking the UI.
    """
    frame_ready = pyqtSignal(object)
    log_message = pyqtSignal(str, str)  # level, message

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.running = False

    def run(self):
        self.log_message.emit("info", f"CameraThread: Starting capture on camera {self.camera_id}")
        self.running = True
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            self.log_message.emit("error", f"CameraThread: Failed to open camera {self.camera_id}")
            self.running = False
            return

        # Set resolution to 1280x720 (720p) if possible
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.log_message.emit("success", "CameraThread: Camera opened successfully")
        
        frame_count = 0
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB for Qt
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame_ready.emit(rgb_frame)
                
                frame_count += 1
                if frame_count % 60 == 0:
                     self.log_message.emit("debug", f"CameraThread: Captured frame {frame_count}")
            else:
                self.log_message.emit("warning", "CameraThread: Failed to read frame")
                self.msleep(100) # Wait a bit before retrying
            
            self.msleep(33)  # ~30 FPS

        cap.release()
        self.log_message.emit("info", "CameraThread: Capture stopped")

    def stop(self):
        self.running = False
        self.wait()

import os
from ultralytics import YOLO
import cv2
import numpy as np

class YoloDetector:
    """
    Wrapper for Ultralytics YOLO model for chess piece detection.
    """
    def __init__(self):
        self.model = None
        self.model_path = None
        self.class_names = {}

    def load_model(self, model_path):
        """
        Loads a YOLO model from the specified path.
        """
        if not os.path.exists(model_path):
            print(f"YoloDetector: Model file not found at {model_path}")
            return False

        try:
            print(f"YoloDetector: Loading model from {model_path}...")
            self.model = YOLO(model_path)
            self.model_path = model_path
            self.class_names = self.model.names
            print(f"YoloDetector: Model loaded successfully. Classes: {self.class_names}")
            return True
        except Exception as e:
            print(f"YoloDetector: Failed to load model: {e}")
            return False

    def detect(self, frame, conf_threshold=0.5):
        """
        Runs detection on the given frame.
        Args:
            frame: RGB image (numpy array)
            conf_threshold: Confidence threshold for detections
        Returns:
            List of detections: [{'class_id': int, 'class_name': str, 'conf': float, 'bbox': [x1, y1, x2, y2]}]
        """
        if self.model is None:
            return []

        results = self.model(frame, conf=conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.class_names.get(cls, str(cls))
                
                detections.append({
                    'class_id': cls,
                    'class_name': class_name,
                    'conf': conf,
                    'bbox': [x1, y1, x2, y2]
                })
                
        return detections

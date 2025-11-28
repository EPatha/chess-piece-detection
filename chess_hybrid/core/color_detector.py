import cv2
import numpy as np

class ColorDetector:
    def __init__(self):
        # Default HSV thresholds (can be tuned)
        # White pieces: High Value, Low Saturation
        self.white_lower = np.array([0, 0, 180])
        self.white_upper = np.array([180, 50, 255])
        
        # Black pieces: Low Value
        self.black_lower = np.array([0, 0, 0])
        self.black_upper = np.array([180, 255, 100])

    def detect_color(self, roi):
        """
        Analyze a Region of Interest (ROI) to determine if it contains a white or black piece.
        Assumes the ROI is already determined to be 'occupied'.
        Returns: 'white', 'black', or 'unknown'
        """
        if roi is None or roi.size == 0:
            return 'unknown'

        # Convert to HSV
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        
        # Extract Value (Brightness) channel
        v_channel = hsv_roi[:, :, 2]
        
        # Calculate mean brightness
        # We can focus on the center of the ROI to avoid background noise
        h, w = v_channel.shape
        center_h, center_w = h // 2, w // 2
        crop_h, crop_w = h // 2, w // 2 # Use 50% of the size
        
        start_y = center_h - crop_h // 2
        start_x = center_w - crop_w // 2
        
        center_crop = v_channel[start_y:start_y+crop_h, start_x:start_x+crop_w]
        
        if center_crop.size == 0:
             mean_val = np.mean(v_channel)
        else:
             mean_val = np.mean(center_crop)
        
        # Threshold for White vs Black
        # This threshold might need tuning. 
        # White pieces are usually > 150 brightness. Black pieces < 100.
        # Let's pick a middle ground.
        brightness_threshold = 120 
        
        # Debug print (optional, can be removed later)
        # print(f"Mean Brightness: {mean_val:.1f}")
        
        if mean_val > brightness_threshold:
            return 'white'
        else:
            return 'black'

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from .color_detector import ColorDetector
from .yolo_detector import YoloDetector

class ProcessingThread(QThread):
    """
    Handles image processing tasks in a background thread.
    Tasks include:
    - Board Auto-Detection (finding corners)
    - Perspective Warping
    - Edge Detection (Canny)
    - Color/Occupancy Analysis
    - YOLO Object Detection (Phase 2)
    """
    move_detected = pyqtSignal(object)
    processed_frame_ready = pyqtSignal(object)
    board_detected = pyqtSignal(list) # List of 4 points [(x,y), ...]
    board_state_updated = pyqtSignal(list) # 8x8 grid of strings
    yolo_state_updated = pyqtSignal(list) # 8x8 grid of YOLO classes
    scan_completed = pyqtSignal(list) # 8x8 grid of stable classes
    debug_corners_detected = pyqtSignal(list) # List of points for debug
    log_message = pyqtSignal(str, str) # level, message

    def __init__(self):
        super().__init__()
        self.running = True
        self.latest_frame = None
        self.canny_lower = 50
        self.canny_upper = 150
        self.is_auto_detecting = False
        self.calibration_points = None
        self.homography_matrix = None
        self.color_detector = ColorDetector()
        self.yolo_detector = YoloDetector() # Phase 2
        self.use_yolo = False
        self.show_raw_warped = False
        self.occupancy_threshold = 50
        self._log_throttle = 0
        
        # Scanning variables
        self.is_scanning = False
        self.scan_frames_count = 0
        self.scan_target_frames = 30 # ~1 second
        self.scan_buffer = [[[] for _ in range(8)] for _ in range(8)]

    def load_yolo_model(self, model_path):
        if self.yolo_detector.load_model(model_path):
            self.use_yolo = True
            print(f"ProcessingThread: YOLO model loaded from {model_path}")
        else:
            self.use_yolo = False
            print("ProcessingThread: Failed to load YOLO model")

    def toggle_yolo(self, enabled):
        self.use_yolo = enabled and (self.yolo_detector.model is not None)

    def run(self):
        while self.running:
            if self.latest_frame is not None:
                try:
                    self.process_frame(self.latest_frame)
                    if self.is_auto_detecting:
                        self.detect_board(self.latest_frame)
                except Exception as e:
                    print(f"ProcessingThread Error: {e}")
                self.latest_frame = None
            self.msleep(10)  # Check for new frames frequently

    def start_auto_detect(self):
        self.is_auto_detecting = True
        print("ProcessingThread: Auto-detection started")

    def stop_auto_detect(self):
        self.is_auto_detecting = False
        print("ProcessingThread: Auto-detection stopped")
        self.debug_corners_detected.emit([]) # Clear debug

    def set_show_raw(self, enabled):
        self.show_raw_warped = enabled

    def update_frame(self, frame):
        self.latest_frame = frame

    def update_params(self, lower, upper):
        self.canny_lower = lower
        self.canny_upper = upper

    def update_occupancy_threshold(self, value):
        self.occupancy_threshold = value
        print(f"ProcessingThread: Occupancy Threshold set to {value}")

    def set_calibration_points(self, points):
        if len(points) != 4:
            return
            
        # Sort points: Top-Left, Top-Right, Bottom-Right, Bottom-Left
        # Simple sorting based on sum(x+y) and diff(y-x)
        pts = np.array(points, dtype="float32")
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        
        self.calibration_points = np.zeros((4, 2), dtype="float32")
        self.calibration_points[0] = pts[np.argmin(s)]      # TL
        self.calibration_points[2] = pts[np.argmax(s)]      # BR
        self.calibration_points[1] = pts[np.argmin(diff)]   # TR
        self.calibration_points[3] = pts[np.argmax(diff)]   # BL
        
        # Compute Homography Matrix
        # Target square size (e.g., 600x600)
        size = 600
        dst_pts = np.array([
            [0, 0],
            [size - 1, 0],
            [size - 1, size - 1],
            [0, size - 1]
        ], dtype="float32")
        
        self.homography_matrix = cv2.getPerspectiveTransform(self.calibration_points, dst_pts)
        print("ProcessingThread: Homography matrix updated")

    def start_scan(self, frames=30):
        self.scan_target_frames = frames
        self.scan_frames_count = 0
        self.scan_buffer = [[[] for _ in range(8)] for _ in range(8)]
        self.is_scanning = True
        print("ProcessingThread: Scanning started...")

    def finish_scan(self):
        self.is_scanning = False
        print("ProcessingThread: Scanning finished.")
        
        # Calculate mode for each square
        result_grid = [[None for _ in range(8)] for _ in range(8)]
        for r in range(8):
            for c in range(8):
                votes = self.scan_buffer[r][c]
                if votes:
                    # Find most frequent class
                    from collections import Counter
                    most_common = Counter(votes).most_common(1)[0][0]
                    result_grid[r][c] = most_common
        
        self.scan_completed.emit(result_grid)

    def process_frame(self, frame):
        if self.homography_matrix is not None:
            # Warp perspective
            warped = cv2.warpPerspective(frame, self.homography_matrix, (600, 600))
            
            # Always perform edge detection for occupancy check
            gray = cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, self.canny_lower, self.canny_upper)

            # Prepare display image
            if self.show_raw_warped:
                display_img = warped.copy()
            else:
                display_img = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            
            # Analyze squares
            square_size = 600 // 8
            
            # YOLO Detection (Phase 2)
            yolo_grid = [[None for _ in range(8)] for _ in range(8)]
            
            if self.use_yolo:
                detections = self.yolo_detector.detect(warped)
                
                # Log detections (throttled)
                self._log_throttle += 1
                if self._log_throttle % 30 == 0: 
                    if detections:
                        counts = {}
                        for d in detections:
                            counts[d['class_name']] = counts.get(d['class_name'], 0) + 1
                        summary = ", ".join([f"{k}:{v}" for k,v in counts.items()])
                        self.log_message.emit("info", f"YOLO: Detected {len(detections)} pieces ({summary})")
                    else:
                        self.log_message.emit("debug", "YOLO: No pieces detected")

                for det in detections:
                    # Get center of bbox
                    x1, y1, x2, y2 = map(int, det['bbox'])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    
                    # Determine square
                    col = cx // square_size
                    row = cy // square_size
                    
                    if 0 <= col < 8 and 0 <= row < 8:
                        yolo_grid[row][col] = det['class_name']
                        
                        # Accumulate for scan
                        if self.is_scanning:
                            self.scan_buffer[row][col].append(det['class_name'])

            # Handle Scan Completion
            if self.is_scanning:
                # Check for occupied but unknown squares
                # We do this by checking edge density for squares that have NO YOLO detection in this frame
                margin = int(square_size * 0.15)
                edge_threshold = self.occupancy_threshold
                
                for row in range(8):
                    for col in range(8):
                        # If we already have a YOLO detection this frame, skip
                        if yolo_grid[row][col]:
                            continue
                            
                        # Check occupancy
                        x1 = col * square_size
                        y1 = row * square_size
                        x2 = (col + 1) * square_size
                        y2 = (row + 1) * square_size
                        
                        roi_x1 = x1 + margin
                        roi_y1 = y1 + margin
                        roi_x2 = x2 - margin
                        roi_y2 = y2 - margin
                        
                        roi_edges = edges[roi_y1:roi_y2, roi_x1:roi_x2]
                        edge_count = cv2.countNonZero(roi_edges)
                        
                        if edge_count > edge_threshold:
                            self.scan_buffer[row][col].append("unknown")
                        else:
                            self.scan_buffer[row][col].append("empty")

                self.scan_frames_count += 1
                if self.scan_frames_count >= self.scan_target_frames:
                    self.finish_scan()

            # Piece Aliases
            aliases = {
                'white-pawn': 'WP', 'white-rook': 'WR', 'white-knight': 'WN',
                'white-bishop': 'WB', 'white-queen': 'WQ', 'white-king': 'WK',
                'black-pawn': 'BP', 'black-rook': 'BR', 'black-knight': 'BN',
                'black-bishop': 'BB', 'black-queen': 'BQ', 'black-king': 'BK'
            }

            board_state = []
            
            # Margin to avoid grid lines (e.g., 10%)
            margin = int(square_size * 0.15)
            
            # Threshold for edge density to consider a square "occupied"
            edge_threshold = self.occupancy_threshold 
            
            for row in range(8):
                row_state = []
                for col in range(8):
                    x1 = col * square_size
                    y1 = row * square_size
                    x2 = (col + 1) * square_size
                    y2 = (row + 1) * square_size
                    
                    # Define inner ROI for analysis (exclude grid lines)
                    roi_x1 = x1 + margin
                    roi_y1 = y1 + margin
                    roi_x2 = x2 - margin
                    roi_y2 = y2 - margin
                    
                    # Extract ROIs
                    roi_color = warped[roi_y1:roi_y2, roi_x1:roi_x2]
                    roi_edges = edges[roi_y1:roi_y2, roi_x1:roi_x2]
                    
                    # 1. Occupancy Detection (Edge Density)
                    edge_count = cv2.countNonZero(roi_edges)
                    is_occupied = edge_count > edge_threshold
                    
                    color = 'empty'
                    if is_occupied:
                        # 2. Color Detection (only if occupied)
                        color = self.color_detector.detect_color(roi_color)
                    
                    row_state.append(color)
                    
                    # Visualize
                    center_x = x1 + square_size // 2
                    center_y = y1 + square_size // 2
                    
                    # Draw Occupancy/Color Indicator (Dots)
                    if color == 'white':
                        cv2.circle(display_img, (center_x, center_y), 10, (255, 255, 255), -1)
                        cv2.circle(display_img, (center_x, center_y), 12, (0, 255, 0), 1)
                    elif color == 'black':
                        cv2.circle(display_img, (center_x, center_y), 10, (0, 0, 0), -1)
                        cv2.circle(display_img, (center_x, center_y), 12, (0, 255, 0), 1)
                        
                    # Draw YOLO Label or Unknown
                    yolo_class = yolo_grid[row][col]
                    label_text = ""
                    label_color = (0, 255, 255) # Yellow default
                    
                    if yolo_class:
                        label_text = aliases.get(yolo_class, yolo_class[:2].upper())
                        label_color = (0, 255, 0) # Green for recognized
                    elif is_occupied and self.use_yolo:
                        label_text = "?" # Unknown
                        label_color = (0, 0, 255) # Red for unknown
                    
                    if label_text:
                        cv2.putText(display_img, label_text, (center_x - 15, center_y + 5), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)

                board_state.append(row_state)
            
            self.board_state_updated.emit(board_state)
            self.yolo_state_updated.emit(yolo_grid)
            
            # Draw 8x8 Grid
            for i in range(1, 8):
                # Vertical lines
                cv2.line(display_img, (i * square_size, 0), (i * square_size, 600), (0, 255, 0), 2)
                # Horizontal lines
                cv2.line(display_img, (0, i * square_size), (600, i * square_size), (0, 255, 0), 2)
            
            self.processed_frame_ready.emit(display_img)
        else:
            # Fallback to full frame edge detection if not calibrated
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, self.canny_lower, self.canny_upper)
            edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            
            self.processed_frame_ready.emit(edges_rgb)

    def detect_board(self, frame):
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Try 1: Standard flags (None) - Strict
        ret, corners = cv2.findChessboardCorners(gray, (7, 7), None)
        
        # Try 2: Adaptive Threshold - More robust to lighting
        if not ret:
            flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FAST_CHECK
            ret, corners = cv2.findChessboardCorners(gray, (7, 7), flags)
        
        if ret:
            print("ProcessingThread: Chessboard pattern found!")
            self.is_auto_detecting = False # Stop scanning
            
            # Refine corners
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            
            # Emit debug corners (all 49 points)
            debug_pts = [tuple(pt[0]) for pt in corners2]
            self.debug_corners_detected.emit(debug_pts)
            
            # corners2 is (49, 1, 2)
            # Extract 4 extreme internal corners
            # Row 0 (Top): indices 0..6
            # Row 6 (Bottom): indices 42..48
            
            # TL (0,0) -> Index 0
            # TR (0,6) -> Index 6
            # BL (6,0) -> Index 42
            # BR (6,6) -> Index 48
            
            p_tl = corners2[0][0]
            p_tr = corners2[6][0]
            p_bl = corners2[42][0]
            p_br = corners2[48][0]
            
            src_pts = np.array([p_tl, p_tr, p_br, p_bl], dtype="float32")
            
            # Define destination points for these internal corners
            # Target image is 600x600. Square size = 75.
            # TL internal (1,1) -> (75, 75)
            dst_pts = np.array([
                [75, 75],
                [525, 75],
                [525, 525],
                [75, 525]
            ], dtype="float32")
            
            # Calculate Homography for internal grid
            H = cv2.getPerspectiveTransform(src_pts, dst_pts)
            
            # Now, find the outer corners of the board (0,0), (600,0), (600,600), (0,600)
            # by mapping them BACK to the source image using inverse homography.
            H_inv = np.linalg.inv(H)
            
            outer_dst = np.array([
                [0, 0],
                [600, 0],
                [600, 600],
                [0, 600]
            ], dtype="float32").reshape(-1, 1, 2)
            
            outer_src = cv2.perspectiveTransform(outer_dst, H_inv)
            
            # Extract points
            outer_points_list = [tuple(pt[0]) for pt in outer_src]
            
            print(f"ProcessingThread: Outer corners: {outer_points_list}")
            
            # Emit these OUTER corners. 
            # MainWindow will pass them to set_calibration_points, which maps them to (0,0)-(600,600).
            # This ensures the final homography matches H.
            self.board_detected.emit(outer_points_list)
            
        else:
            # Only print occasionally to avoid spamming logs too hard, or just print
            # print("ProcessingThread: Chessboard pattern not found. Ensure board is EMPTY.")
            pass

    def stop(self):
        self.running = False
        self.wait()

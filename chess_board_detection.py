#!/usr/bin/env python3
"""
Chess Board Detection - Detect 64 squares and identify pieces
Output format:
- Capital letters (R,N,B,Q,K,P) = White pieces
- Lowercase letters (r,n,b,q,k,p) = Black pieces  
- Dot (.) = Empty square
"""
import cv2
import numpy as np
from ultralytics import YOLO
import sys


class ChessBoardDetector:
    """Detect chessboard and identify pieces in 64 squares"""
    
    def __init__(self, model_path="runs/chess_detect/train3/weights/best.pt"):
        """Initialize detector with YOLOv8 model"""
        self.model = YOLO(model_path)
        
        # Mapping from YOLOv8 class names to chess notation
        # Based on actual model class names
        self.piece_map = {
            'bishop': '.',  # Ambiguous, treat as empty
            'black-bishop': 'b',
            'black-king': 'k',
            'black-knight': 'n',
            'black-pawn': 'p',
            'black-queen': 'q',
            'black-rook': 'r',
            'white-bishop': 'B',
            'white-king': 'K',
            'white-knight': 'N',
            'white-pawn': 'P',
            'white-queen': 'Q',
            'white-rook': 'R',
        }
    
    def detect_board_corners(self, image):
        """
        Detect chessboard corners using contour detection
        Returns: 4 corner points (top-left, top-right, bottom-right, bottom-left)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the largest quadrilateral contour (chessboard)
        board_contour = None
        max_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area:
                # Approximate contour to polygon
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                # Check if it's a quadrilateral
                if len(approx) == 4:
                    board_contour = approx
                    max_area = area
        
        if board_contour is None:
            # Fallback: use entire image
            h, w = image.shape[:2]
            return np.array([
                [0, 0],
                [w, 0],
                [w, h],
                [0, h]
            ], dtype=np.float32)
        
        # Order points: top-left, top-right, bottom-right, bottom-left
        points = board_contour.reshape(4, 2).astype(np.float32)
        ordered = self.order_points(points)
        
        return ordered
    
    def order_points(self, pts):
        """Order points in clockwise order starting from top-left"""
        # Sort by y-coordinate
        sorted_pts = pts[np.argsort(pts[:, 1])]
        
        # Top two points
        top = sorted_pts[:2]
        # Bottom two points
        bottom = sorted_pts[2:]
        
        # Sort top points by x (left to right)
        top = top[np.argsort(top[:, 0])]
        # Sort bottom points by x (right to left for clockwise)
        bottom = bottom[np.argsort(bottom[:, 0])[::-1]]
        
        # Return: top-left, top-right, bottom-right, bottom-left
        return np.array([top[0], top[1], bottom[0], bottom[1]], dtype=np.float32)
    
    def get_square_centers(self, corners):
        """
        Calculate center points of all 64 squares
        Returns: 8x8 array of (x, y) coordinates
        """
        # Define destination points for perspective transform (800x800 square)
        size = 800
        dst = np.array([
            [0, 0],
            [size, 0],
            [size, size],
            [0, size]
        ], dtype=np.float32)
        
        # Get perspective transform matrix
        M = cv2.getPerspectiveTransform(corners, dst)
        
        # Calculate centers of 64 squares in the warped image
        square_size = size / 8
        centers = []
        
        for row in range(8):
            row_centers = []
            for col in range(8):
                # Center of each square in warped coordinates
                center_x = (col + 0.5) * square_size
                center_y = (row + 0.5) * square_size
                
                # Transform back to original image coordinates
                point = np.array([[[center_x, center_y]]], dtype=np.float32)
                M_inv = cv2.getPerspectiveTransform(dst, corners)
                original_point = cv2.perspectiveTransform(point, M_inv)
                
                row_centers.append(original_point[0][0])
            
            centers.append(row_centers)
        
        return np.array(centers)
    
    def get_square_regions(self, image, corners):
        """
        Extract 64 square regions from the image
        Returns: 8x8 array of image patches
        """
        # Warp perspective to get top-down view
        size = 800
        dst = np.array([
            [0, 0],
            [size, 0],
            [size, size],
            [0, size]
        ], dtype=np.float32)
        
        M = cv2.getPerspectiveTransform(corners, dst)
        warped = cv2.warpPerspective(image, M, (size, size))
        
        # Split into 8x8 grid
        square_size = size // 8
        squares = []
        
        for row in range(8):
            row_squares = []
            for col in range(8):
                y1 = row * square_size
                y2 = (row + 1) * square_size
                x1 = col * square_size
                x2 = (col + 1) * square_size
                
                square = warped[y1:y2, x1:x2]
                row_squares.append(square)
            
            squares.append(row_squares)
        
        return np.array(squares), warped
    
    def detect_piece_in_square(self, square_image, conf_threshold=0.15):
        """
        Detect chess piece in a single square using YOLO
        Returns: piece notation (e.g., 'P', 'n', '.')
        """
        # Run YOLO inference
        results = self.model(square_image, conf=conf_threshold, verbose=False)
        
        # Get detections
        if len(results) == 0 or len(results[0].boxes) == 0:
            return '.'  # Empty square
        
        # Get highest confidence detection
        boxes = results[0].boxes
        confidences = boxes.conf.cpu().numpy()
        best_idx = np.argmax(confidences)
        
        # Get class name
        class_id = int(boxes.cls[best_idx].cpu().numpy())
        class_name = self.model.names[class_id]
        
        # Map to chess notation
        return self.piece_map.get(class_name, '.')
    
    def detect_board_state(self, image, conf_threshold=0.15):
        """
        Detect full board state
        Returns: 8x8 array of piece notations
        """
        # Detect board corners
        corners = self.detect_board_corners(image)
        
        # Get square regions
        squares, warped = self.get_square_regions(image, corners)
        
        # Detect pieces in each square
        board_state = []
        
        print("\n🔍 Detecting pieces in 64 squares...\n")
        
        for row_idx, row in enumerate(squares):
            row_state = []
            for col_idx, square in enumerate(row):
                piece = self.detect_piece_in_square(square, conf_threshold)
                row_state.append(piece)
                
                # Progress indicator
                square_num = row_idx * 8 + col_idx + 1
                print(f"\rProgress: {square_num}/64 squares", end='')
            
            board_state.append(row_state)
        
        print("\n")
        return np.array(board_state), warped, corners
    
    def print_board(self, board_state):
        """Print board state in readable format"""
        print("\n" + "="*40)
        print("  CHESS BOARD STATE")
        print("="*40)
        print("\n  a b c d e f g h")
        print("  ---------------")
        
        for idx, row in enumerate(board_state):
            rank = 8 - idx  # Chess ranks go 8->1 from top to bottom
            print(f"{rank} {' '.join(row)}")
        
        print("\n" + "="*40)
        print("Legend:")
        print("  Capital (R,N,B,Q,K,P) = White pieces")
        print("  Lowercase (r,n,b,q,k,p) = Black pieces")
        print("  Dot (.) = Empty square")
        print("="*40 + "\n")
    
    def save_visualization(self, image, board_state, corners, warped, output_path="board_detection.jpg"):
        """Save visualization of detection"""
        # Draw corners on original image
        vis_image = image.copy()
        
        # Draw board outline
        corners_int = corners.astype(np.int32)
        cv2.polylines(vis_image, [corners_int], True, (0, 255, 0), 3)
        
        # Draw corner points
        for corner in corners_int:
            cv2.circle(vis_image, tuple(corner), 10, (0, 0, 255), -1)
        
        # Create side-by-side visualization
        h, w = vis_image.shape[:2]
        
        # Add text on warped board
        square_size = warped.shape[0] // 8
        annotated_warped = warped.copy()
        
        for row_idx, row in enumerate(board_state):
            for col_idx, piece in enumerate(row):
                if piece != '.':
                    # Draw piece notation on square
                    x = col_idx * square_size + square_size // 2 - 15
                    y = row_idx * square_size + square_size // 2 + 15
                    
                    color = (255, 255, 255) if piece.isupper() else (0, 0, 0)
                    cv2.putText(annotated_warped, piece, (x, y),
                              cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        
        # Resize warped to match original height
        warped_resized = cv2.resize(annotated_warped, (h, h))
        
        # Combine images
        combined = np.hstack([vis_image, warped_resized])
        
        # Save
        cv2.imwrite(output_path, combined)
        print(f"✅ Visualization saved to: {output_path}")


def main():
    """Main function for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 chess_board_detection.py <image_path> [confidence_threshold]")
        print("\nExample:")
        print("  python3 chess_board_detection.py chessboard.jpg 0.15")
        sys.exit(1)
    
    image_path = sys.argv[1]
    conf_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15
    
    print("\n" + "="*60)
    print("  🎯 Chess Board Detection")
    print("="*60)
    print(f"\n📷 Image: {image_path}")
    print(f"🎚️  Confidence: {conf_threshold}")
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"\n❌ Error: Could not load image: {image_path}")
        sys.exit(1)
    
    print(f"✅ Image loaded: {image.shape[1]}x{image.shape[0]}")
    
    # Create detector
    detector = ChessBoardDetector()
    
    # Detect board state
    board_state, warped, corners = detector.detect_board_state(image, conf_threshold)
    
    # Print board
    detector.print_board(board_state)
    
    # Save visualization
    output_path = image_path.replace('.', '_detected.')
    detector.save_visualization(image, board_state, corners, warped, output_path)
    
    # Generate FEN-like notation (optional)
    print("📋 Board state (FEN-like):")
    for row in board_state:
        print(' '.join(row))
    
    print("\n✅ Detection complete!\n")


if __name__ == "__main__":
    main()

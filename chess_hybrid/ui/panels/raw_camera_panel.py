from .base_panel import BasePanel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush

class RawCameraPanel(BasePanel):
    calibration_point_clicked = pyqtSignal(int, int) # x, y

    def __init__(self):
        super().__init__("Raw Camera View")
        self.calibration_mode = False
        self.calibration_points = None
        self.debug_points = []
        
    def set_calibration_mode(self, active):
        self.calibration_mode = active
        if active:
            self.image_label.setCursor(Qt.CrossCursor)
        else:
            self.image_label.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if self.calibration_mode:
            # Map click to image_label coordinates
            lbl_pos = self.image_label.mapFrom(self, event.pos())
            x = lbl_pos.x()
            y = lbl_pos.y()
            
            # Map widget coordinates to image coordinates
            if self.image_label.pixmap() and hasattr(self, 'original_size'):
                lbl_size = self.image_label.size()
                pix_size = self.image_label.pixmap().size()
                
                # The pixmap is already scaled to fit lbl_size while keeping aspect ratio
                # and is centered in the label.
                
                # Calculate offsets (centering)
                x_offset = (lbl_size.width() - pix_size.width()) // 2
                y_offset = (lbl_size.height() - pix_size.height()) // 2
                
                # Click coordinates relative to the pixmap
                click_x_pix = x - x_offset
                click_y_pix = y - y_offset
                
                # Check if click is within the pixmap
                if 0 <= click_x_pix < pix_size.width() and 0 <= click_y_pix < pix_size.height():
                    # Scale to original image coordinates
                    orig_w, orig_h = self.original_size
                    
                    img_x = int(click_x_pix * (orig_w / pix_size.width()))
                    img_y = int(click_y_pix * (orig_h / pix_size.height()))
                    
                    # Clamp to be safe
                    img_x = max(0, min(img_x, orig_w - 1))
                    img_y = max(0, min(img_y, orig_h - 1))
                    
                    self.calibration_point_clicked.emit(img_x, img_y)

    def set_detected_points(self, points):
        self.calibration_points = points
        self.update() # Trigger repaint
        
    def set_debug_points(self, points):
        self.debug_points = points
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.image_label.pixmap():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            lbl_size = self.image_label.size()
            pix_size = self.image_label.pixmap().size()
            scaled_pix_size = pix_size.scaled(lbl_size, Qt.KeepAspectRatio)
            x_offset = (lbl_size.width() - scaled_pix_size.width()) // 2
            y_offset = (lbl_size.height() - scaled_pix_size.height()) // 2
            
            scale_x = scaled_pix_size.width() / pix_size.width()
            scale_y = scaled_pix_size.height() / pix_size.height()
            
            # Draw Debug Points (Red)
            if self.debug_points:
                painter.setPen(QPen(Qt.red, 2))
                painter.setBrush(QBrush(Qt.red))
                for pt in self.debug_points:
                    x = int(pt[0] * scale_x + x_offset)
                    y = int(pt[1] * scale_y + y_offset)
                    painter.drawEllipse(x - 2, y - 2, 4, 4)

            # Draw calibration points (Green)
            if self.calibration_points:
                painter.setPen(QPen(Qt.green, 3))
                painter.setBrush(QBrush(Qt.green))
                
                mapped_points = []
                for pt in self.calibration_points:
                    x = int(pt[0] * scale_x + x_offset)
                    y = int(pt[1] * scale_y + y_offset)
                    mapped_points.append((x, y))
                    painter.drawEllipse(x - 5, y - 5, 10, 10)
                
                # Draw lines connecting points if we have 4
                if len(mapped_points) == 4:
                    painter.setPen(QPen(Qt.green, 2))
                    # Assuming TL, TR, BR, BL order (or whatever order they come in)
                    # If they are sorted, we can draw a quad.
                    # Let's just draw a loop 0-1-2-3-0
                    for i in range(4):
                        p1 = mapped_points[i]
                        p2 = mapped_points[(i + 1) % 4]
                        painter.drawLine(p1[0], p1[1], p2[0], p2[1])

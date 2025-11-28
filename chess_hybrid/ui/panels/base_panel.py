from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt

class BasePanel(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Title overlay
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            color: white;
            font-size: 14pt;
            font-weight: bold;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(title_label) # Changed from header to title_label
        
        # Placeholder
        self.placeholder = QLabel("No Signal")
        self.placeholder.setObjectName("placeholder")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.placeholder)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.hide() # Hide initially
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setMinimumSize(100, 100) # Prevent collapsing
        self.layout.addWidget(self.image_label)
        
        # self.layout.addStretch() # Removed to allow expansion
        self.setLayout(self.layout)

    def update_frame(self, frame):
        # Convert numpy array (RGB) to QImage/QPixmap and display
        if frame is None:
            self.image_label.hide()
            self.placeholder.show()
            return
            
        from PyQt5.QtGui import QImage, QPixmap
        
        # Frame received
        self.placeholder.hide()
        self.image_label.show()
        
        h, w, ch = frame.shape
        self.original_size = (w, h)
        bytes_per_line = ch * w
        
        # Debug: Print frame info once every 30 frames to avoid spam
        if not hasattr(self, '_frame_count'):
            self._frame_count = 0
        self._frame_count += 1
        if self._frame_count % 30 == 0:
            print(f"Panel '{self.title}': Received frame {w}x{h}, mean val: {frame.mean():.1f}")

        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # Copy image to ensure data persistence
        q_img = q_img.copy() 
        
        self.image_label.setPixmap(QPixmap.fromImage(q_img).scaled(
            self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

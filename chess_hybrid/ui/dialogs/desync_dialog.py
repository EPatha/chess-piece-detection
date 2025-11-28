from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class DesyncDialog(QDialog):
    def __init__(self, move_uci, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Desynchronization Detected")
        self.resize(400, 200)
        self.setStyleSheet("background-color: #2B2B2B; color: white;")
        
        layout = QVBoxLayout(self)
        
        # Warning Icon/Text
        title = QLabel("⚠️ Illegal Move Detected")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF5252;")
        layout.addWidget(title)
        
        msg = QLabel(f"The system detected a move <b>{move_uci}</b> which is illegal in the current position.<br><br>"
                     "This usually means the vision system is desynchronized from the real board.")
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 14px;")
        layout.addWidget(msg)
        
        layout.addStretch()
        
        # Options
        self.result_action = None
        
        btn_layout = QVBoxLayout()
        
        undo_btn = QPushButton("Undo Last Move (Recommended)")
        undo_btn.setStyleSheet("background-color: #FF9800; color: black; padding: 8px;")
        undo_btn.clicked.connect(lambda: self.finish("undo"))
        btn_layout.addWidget(undo_btn)
        
        manual_btn = QPushButton("Manual Correction")
        manual_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        manual_btn.clicked.connect(lambda: self.finish("manual"))
        btn_layout.addWidget(manual_btn)
        
        ignore_btn = QPushButton("Ignore (Dismiss)")
        ignore_btn.setStyleSheet("background-color: #757575; color: white; padding: 8px;")
        ignore_btn.clicked.connect(lambda: self.finish("ignore"))
        btn_layout.addWidget(ignore_btn)
        
        layout.addLayout(btn_layout)
        
    def finish(self, action):
        self.result_action = action
        self.accept()

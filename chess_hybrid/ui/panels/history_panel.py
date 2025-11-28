from .base_panel import BasePanel
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout
from PyQt5.QtGui import QFont

class HistoryPanel(BasePanel):
    def __init__(self):
        super().__init__("Move History")
        
    def setup_ui(self):
        super().setup_ui()
        # Remove BasePanel widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; border: none; font-family: 'Courier New';")
        self.text_edit.setFont(QFont("Courier New", 12))
        
        self.layout.addWidget(self.text_edit)

    def update_history(self, pgn_text):
        # PGN text contains headers and moves. We just want the moves part usually, 
        # but displaying the whole PGN is also fine and simple.
        # Or we can format it nicely.
        self.text_edit.setText(pgn_text)
        
        # Scroll to bottom
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.End)
        self.text_edit.setTextCursor(cursor)

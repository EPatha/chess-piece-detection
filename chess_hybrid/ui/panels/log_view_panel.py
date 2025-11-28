from PyQt5.QtWidgets import QPlainTextEdit, QVBoxLayout
from .base_panel import BasePanel
import datetime

class LogViewPanel(BasePanel):
    def __init__(self):
        super().__init__("Log View")
        
    def setup_ui(self):
        super().setup_ui()
        # Remove BasePanel widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.insertWidget(1, self.log_text) # Insert below title
        
    def add_entry(self, level, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color = "#FFFFFF" # Default white
        
        if level == "error": color = "#FF0000"
        elif level == "warning": color = "#FFFF00"
        elif level == "success": color = "#00FF00"
        elif level == "debug": color = "#808080"
        elif level == "info": color = "#00FFFF"
        
        formatted_msg = f'<span style="color:{color}">[{timestamp}] {message}</span>'
        self.log_text.appendHtml(formatted_msg)

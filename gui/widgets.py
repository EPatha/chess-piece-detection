"""Custom GUI widgets."""
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal


class ClickableLabel(QLabel):
    """Label that emits click events with position."""
    clicked = pyqtSignal(int, int)
    
    def mousePressEvent(self, event):
        self.clicked.emit(event.x(), event.y())

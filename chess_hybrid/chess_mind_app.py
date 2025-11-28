import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import STYLESHEET

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

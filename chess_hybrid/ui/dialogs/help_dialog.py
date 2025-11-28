from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ChessMind Hybrid - Help")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setHtml("""
            <h1>ChessMind Hybrid Vision System</h1>
            <p>Welcome to ChessMind Hybrid! This system digitizes your physical chessboard in real-time.</p>
            
            <h2>Keyboard Shortcuts</h2>
            <ul>
                <li><b>U</b>: Undo Last Move</li>
                <li><b>R</b>: Reset Game</li>
                <li><b>M</b>: Manual Correction Dialog</li>
            </ul>
            
            <h2>Quick Start</h2>
            <ol>
                <li><b>Select Camera</b>: Choose your webcam from the dropdown.</li>
                <li><b>Calibrate</b>: Click 'AUTO DETECT' or 'MANUAL CALIBRATE' to set the board corners.</li>
                <li><b>Play</b>: Make moves on the board. Wait for the 'Stability' indicator to confirm.</li>
            </ol>
            
            <h2>Features</h2>
            <ul>
                <li><b>Stockfish Analysis</b>: Enable to see evaluation and best move arrows.</li>
                <li><b>Play vs AI</b>: Choose a mode to play against the computer.</li>
                <li><b>Manual Correction</b>: Use this if the vision system gets confused.</li>
            </ul>
            
            <p><i>For more details, refer to the <b>walkthrough.md</b> file.</i></p>
        """)
        layout.addWidget(self.text_browser)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

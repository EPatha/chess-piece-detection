from .base_panel import BasePanel
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QProgressBar
from PyQt5.QtCore import Qt

class EvaluationPanel(BasePanel):
    def __init__(self):
        super().__init__("Engine Evaluation")
        
    def setup_ui(self):
        super().setup_ui()
        # Remove BasePanel widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        content_layout = QVBoxLayout()
        
        self.score_label = QLabel("Evaluation: N/A")
        self.score_label.setStyleSheet("font-size: 20px; color: white; font-weight: bold;")
        self.score_label.setAlignment(Qt.AlignCenter)
        
        self.bar = QProgressBar()
        self.bar.setRange(-1000, 1000) # -10.00 to +10.00
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: #212121;
            }
            QProgressBar::chunk {
                background-color: #FFFFFF;
            }
        """)
        
        content_layout.addWidget(self.score_label)
        content_layout.addWidget(self.bar)
        content_layout.addStretch()
        
        self.layout.addLayout(content_layout)

    def update_evaluation(self, score_str):
        self.score_label.setText(f"Eval: {score_str}")
        
        # Parse score for bar
        try:
            if score_str.startswith("M"):
                # Mate
                mate_in = int(score_str[1:])
                val = 1000 if mate_in > 0 else -1000
            else:
                val = float(score_str) * 100 # Scale to bar range
                val = max(-1000, min(1000, val))
            
            self.bar.setValue(int(val))
            
            # Change color based on advantage
            if val > 0:
                self.bar.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid grey;
                        border-radius: 5px;
                        background-color: #212121;
                    }
                    QProgressBar::chunk {
                        background-color: #FFFFFF; 
                    }
                """)
            else:
                 # Invert for black advantage? 
                 # Standard bar fills from left. 
                 # Let's keep it simple: White advantage fills from left (White).
                 # Black advantage... actually QProgressBar isn't great for centered 0.
                 # But for MVP, let's just show the value.
                 pass
                 
        except ValueError:
            pass

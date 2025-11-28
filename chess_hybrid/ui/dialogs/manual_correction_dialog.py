from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QPushButton, QLabel, QComboBox, QDialogButtonBox)
from PyQt5.QtCore import Qt
import chess

class ManualCorrectionDialog(QDialog):
    def __init__(self, current_fen, parent=None, unknown_squares=None):
        super().__init__(parent)
        self.setWindowTitle("Manual State Correction")
        self.resize(600, 600)
        
        self.board = chess.Board(current_fen)
        self.unknown_squares = unknown_squares or []
        self.selected_square = None
        
        self.layout = QVBoxLayout(self)
        
        # Instructions
        self.layout.addWidget(QLabel("Click a square to edit its piece. Red squares were detected as occupied but unknown."))
        
        # Board Grid
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.buttons = {}
        
        self.piece_map = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
            None: ' '
        }
        
        # Create 8x8 grid of buttons
        for rank in range(7, -1, -1):
            for file in range(8):
                square = chess.square(file, rank)
                btn = QPushButton()
                btn.setFixedSize(60, 60)
                btn.setStyleSheet(self.get_square_style(square))
                btn.clicked.connect(lambda _, s=square: self.on_square_clicked(s))
                
                self.grid_layout.addWidget(btn, 7-rank, file)
                self.buttons[square] = btn
                
        self.update_board_display()
        self.layout.addLayout(self.grid_layout)
        
        # Turn Selector
        turn_layout = QHBoxLayout()
        turn_layout.addWidget(QLabel("Side to Move:"))
        self.turn_combo = QComboBox()
        self.turn_combo.addItems(["White", "Black"])
        self.turn_combo.setCurrentIndex(0 if self.board.turn == chess.WHITE else 1)
        turn_layout.addWidget(self.turn_combo)
        self.layout.addLayout(turn_layout)
        
        # Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
        
    def get_square_style(self, square):
        rank = chess.square_rank(square)
        file = chess.square_file(square)
        is_light = (rank + file) % 2 != 0
        color = "#F0D9B5" if is_light else "#B58863"
        return f"""
            QPushButton {{
                background-color: {color};
                border: none;
                font-size: 30px;
                color: black;
            }}
            QPushButton:hover {{
                border: 2px solid blue;
            }}
        """

    def update_board_display(self):
        for square, btn in self.buttons.items():
            piece = self.board.piece_at(square)
            symbol = self.piece_map.get(piece.symbol() if piece else None, ' ')
            btn.setText(symbol)
            
            style = self.get_square_style(square)
            
            # Highlight unknown squares
            if square in self.unknown_squares:
                style = style.replace("border: none;", "border: 3px solid red;")
                if not piece:
                    btn.setText("?")
            
            # Color the text
            if piece:
                style = style.replace("color: black;", "color: black; font-weight: bold;")
            
            btn.setStyleSheet(style)

    def on_square_clicked(self, square):
        # Show a popup to select piece
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        
        actions = [
            ("Clear", None),
            ("White Pawn", 'P'), ("White Knight", 'N'), ("White Bishop", 'B'), ("White Rook", 'R'), ("White Queen", 'Q'), ("White King", 'K'),
            ("Black Pawn", 'p'), ("Black Knight", 'n'), ("Black Bishop", 'b'), ("Black Rook", 'r'), ("Black Queen", 'q'), ("Black King", 'k')
        ]
        
        for name, symbol in actions:
            action = menu.addAction(name)
            action.setData(symbol)
            
        action = menu.exec_(self.buttons[square].mapToGlobal(self.buttons[square].rect().center()))
        
        if action:
            symbol = action.data()
            if symbol:
                self.board.set_piece_at(square, chess.Piece.from_symbol(symbol))
            else:
                self.board.remove_piece_at(square)
            self.update_board_display()

    def get_fen(self):
        # Update turn
        self.board.turn = chess.WHITE if self.turn_combo.currentIndex() == 0 else chess.BLACK
        return self.board.fen()

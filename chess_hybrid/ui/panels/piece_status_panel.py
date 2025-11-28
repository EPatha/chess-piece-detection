from .base_panel import BasePanel
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

class PieceStatusPanel(BasePanel):
    def __init__(self):
        super().__init__("Pieces Status Log")
        
    def setup_ui(self):
        super().setup_ui()
        # Remove BasePanel widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8) # Reduced spacing
        
        # Turn Indicator
        self.turn_label = QLabel("Turn: White")
        self.turn_label.setAlignment(Qt.AlignCenter)
        self.turn_label.setStyleSheet("font-size: 18px; color: #4CAF50; font-weight: bold; background-color: #2e2e2e; padding: 10px; border-radius: 5px;")
        
        # Clock
        self.clock_widget = QWidget()
        clock_layout = QHBoxLayout(self.clock_widget)
        clock_layout.setContentsMargins(0, 0, 0, 0)
        
        clock_style = """
            font-family: 'Courier New', monospace;
            font-size: 28px;
            font-weight: bold;
            color: white;
            background-color: #222;
            padding: 5px 15px;
            border: 2px solid #444;
            border-radius: 5px;
        """
        
        self.white_clock = QLabel("10:00")
        self.white_clock.setStyleSheet(clock_style)
        self.white_clock.setAlignment(Qt.AlignCenter)
        
        self.black_clock = QLabel("10:00")
        self.black_clock.setStyleSheet(clock_style)
        self.black_clock.setAlignment(Qt.AlignCenter)
        
        # Clock Containers with Labels
        w_clock_cont = QVBoxLayout()
        w_lbl = QLabel("WHITE")
        w_lbl.setStyleSheet("color: #aaa; font-size: 10px; font-weight: bold;")
        w_lbl.setAlignment(Qt.AlignCenter)
        w_clock_cont.addWidget(w_lbl)
        w_clock_cont.addWidget(self.white_clock)
        
        b_clock_cont = QVBoxLayout()
        b_lbl = QLabel("BLACK")
        b_lbl.setStyleSheet("color: #aaa; font-size: 10px; font-weight: bold;")
        b_lbl.setAlignment(Qt.AlignCenter)
        b_clock_cont.addWidget(b_lbl)
        b_clock_cont.addWidget(self.black_clock)
        
        clock_layout.addLayout(w_clock_cont)
        clock_layout.addStretch()
        clock_layout.addLayout(b_clock_cont)
        
        self.clock_widget.hide() # Hidden by default
        content_layout.addWidget(self.clock_widget)
        
        # Move Count
        self.move_label = QLabel("Move: 1")
        self.move_label.setAlignment(Qt.AlignCenter)
        self.move_label.setStyleSheet("font-size: 14px; color: #888;")
        content_layout.addWidget(self.move_label)
        
        # Material Difference
        self.material_label = QLabel("Material: Equal")
        self.material_label.setAlignment(Qt.AlignCenter)
        self.material_label.setStyleSheet("font-size: 16px; color: #FFC107; font-weight: bold; margin-top: 10px;")
        content_layout.addWidget(self.material_label)
        
        # Captured Pieces Area
        captured_layout = QVBoxLayout()
        captured_layout.setSpacing(5)
        
        # White Lost (Black captured)
        w_lost_row = QHBoxLayout()
        w_lost_lbl = QLabel("White Lost:")
        w_lost_lbl.setStyleSheet("color: #aaa; font-size: 12px;")
        self.white_lost_display = QLabel("")
        self.white_lost_display.setStyleSheet("color: #ddd; font-size: 20px;")
        w_lost_row.addWidget(w_lost_lbl)
        w_lost_row.addWidget(self.white_lost_display)
        w_lost_row.addStretch()
        
        # Black Lost (White captured)
        b_lost_row = QHBoxLayout()
        b_lost_lbl = QLabel("Black Lost:")
        b_lost_lbl.setStyleSheet("color: #aaa; font-size: 12px;")
        self.black_lost_display = QLabel("")
        self.black_lost_display.setStyleSheet("color: #ddd; font-size: 20px;")
        b_lost_row.addWidget(b_lost_lbl)
        b_lost_row.addWidget(self.black_lost_display)
        b_lost_row.addStretch()
        
        captured_layout.addLayout(w_lost_row)
        captured_layout.addLayout(b_lost_row)
        
        captured_group = QWidget() # Just a container
        captured_group.setLayout(captured_layout)
        # captured_group.setStyleSheet("background-color: #252525; border-radius: 5px; padding: 5px;") # Removed ghost background
        content_layout.addWidget(captured_group)
        
        content_layout.addWidget(self.turn_label) # Move turn label to bottom or top? User said "top of board view".
        # Let's keep turn label at top actually.
        
        # Re-arrange: Turn -> Clock -> Move -> Material -> Captured
        final_layout = QVBoxLayout()
        final_layout.addWidget(self.turn_label)
        final_layout.addLayout(content_layout)
        final_layout.addStretch()
        
        self.layout.addLayout(final_layout)

    def update_state(self, state):
        pass

    def update_game_info(self, fen):
        import chess
        board = chess.Board(fen)
        
        # Turn
        turn_text = "WHITE TO MOVE" if board.turn == chess.WHITE else "BLACK TO MOVE"
        turn_bg = "#4CAF50" if board.turn == chess.WHITE else "#444"
        turn_fg = "white"
        
        if board.is_checkmate():
            turn_text = "CHECKMATE"
            turn_bg = "#F44336"
        elif board.is_check():
            turn_text = "CHECK"
            turn_bg = "#FF9800"
            
        self.turn_label.setText(turn_text)
        self.turn_label.setStyleSheet(f"font-size: 18px; color: {turn_fg}; font-weight: bold; background-color: {turn_bg}; padding: 10px; border-radius: 5px;")
            
        # Move
        self.move_label.setText(f"Move {board.fullmove_number}")
        
        # Captured Pieces
        starting_pieces = {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}
        current_white = {k: 0 for k in starting_pieces}
        current_black = {k: 0 for k in starting_pieces}
        
        for piece in board.piece_map().values():
            if piece.piece_type == chess.KING: continue
            if piece.color == chess.WHITE:
                current_white[piece.piece_type] += 1
            else:
                current_black[piece.piece_type] += 1
                
        piece_symbols = {chess.PAWN: '♙', chess.KNIGHT: '♘', chess.BISHOP: '♗', chess.ROOK: '♖', chess.QUEEN: '♕'}
        
        # White pieces lost (captured by Black)
        w_lost = []
        for pt in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
            count = starting_pieces[pt] - current_white[pt]
            if count > 0: w_lost.extend([piece_symbols[pt]] * count)
            
        # Black pieces lost (captured by White)
        b_lost = []
        for pt in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
            count = starting_pieces[pt] - current_black[pt]
            if count > 0: b_lost.extend([piece_symbols[pt]] * count)
            
        self.white_lost_display.setText(" ".join(w_lost))
        self.black_lost_display.setText(" ".join(b_lost))
        
        # Material
        values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
        w_score = sum(current_white[pt] * values[pt] for pt in current_white)
        b_score = sum(current_black[pt] * values[pt] for pt in current_black)
        diff = w_score - b_score
        
        if diff > 0: self.material_label.setText(f"Material: +{diff} (White)")
        elif diff < 0: self.material_label.setText(f"Material: +{abs(diff)} (Black)")
        else: self.material_label.setText("Material: Equal")

    def update_clock(self, white_time, black_time):
        def fmt(t):
            m = int(t // 60)
            s = int(t % 60)
            return f"{m:02d}:{s:02d}"
            
        self.white_clock.setText(fmt(white_time))
        self.black_clock.setText(fmt(black_time))

    def toggle_clock(self, visible):
        if visible:
            self.clock_widget.show()
        else:
            self.clock_widget.hide()

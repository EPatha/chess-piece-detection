from .base_panel import BasePanel
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QRectF

class BoardViewPanel(BasePanel):
    def __init__(self):
        super().__init__("Board View")
        self.board_state = None # FEN string
        self.last_move = None # UCI string
        self.best_move = None # UCI string
        self.is_flipped = False

    def setup_ui(self):
        # BoardViewPanel draws everything itself, so we don't need BasePanel's widgets
        super().setup_ui()
        # Remove all widgets from the layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def update_fen(self, fen, last_move_uci=""):
        self.board_state = fen
        self.last_move = last_move_uci
        self.best_move = None # Clear best move on new state
        self.update()

    def set_best_move(self, move_uci):
        self.best_move = move_uci
        self.update()
        
    def flip_board(self):
        self.is_flipped = not self.is_flipped
        self.update()

    def update_state(self, state):
        # Legacy method compatibility if needed, but we prefer update_fen
        pass

    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw Board Background
        rect = self.rect()
        # Maximize board size: use almost full available space
        # Leave small padding for coordinates (20px is enough if we position them inside or tight)
        # Coordinates take about 20px on sides.
        padding = 25 
        board_size = min(rect.width(), rect.height()) - padding
        
        x_start = (rect.width() - board_size) // 2
        y_start = (rect.height() - board_size) // 2
        
        square_size = board_size / 8
        
        # Helper for coordinates
        file_map = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
        def get_rc(sq):
            c = file_map[sq[0]]
            r = 7 - (int(sq[1]) - 1)
            return r, c
            
        def get_xy(r, c):
            # If flipped, rotate 180 degrees
            if self.is_flipped:
                r = 7 - r
                c = 7 - c
            return x_start + c * square_size, y_start + r * square_size

        # Draw Squares
        for row in range(8):
            for col in range(8):
                x, y = get_xy(row, col)
                
                color = QColor("#F0D9B5") if (row + col) % 2 == 0 else QColor("#B58863")
                painter.fillRect(int(x), int(y), int(square_size), int(square_size), color)
                
                # Highlight last move
                if self.last_move:
                    try:
                        src_sq = self.last_move[:2]
                        dst_sq = self.last_move[2:4]
                        src_r, src_c = get_rc(src_sq)
                        dst_r, dst_c = get_rc(dst_sq)
                        
                        if (row == src_r and col == src_c) or (row == dst_r and col == dst_c):
                            highlight = QColor(255, 255, 0, 100) # Yellow transparent
                            painter.fillRect(int(x), int(y), int(square_size), int(square_size), highlight)
                    except:
                        pass

        # Draw Coordinates
        painter.setPen(QColor("#888888"))
        font = painter.font()
        font.setPixelSize(12)
        painter.setFont(font)
        
        # Files (a-h)
        for col in range(8):
            char = chr(ord('a') + col)
            if self.is_flipped:
                char = chr(ord('h') - col)
            
            x = x_start + col * square_size
            y = y_start + board_size + 15
            rect = QRectF(x, y, square_size, 20)
            painter.drawText(rect, Qt.AlignCenter, char)
            
        # Ranks (1-8)
        for row in range(8):
            char = str(8 - row)
            if self.is_flipped:
                char = str(row + 1)
                
            x = x_start - 20
            y = y_start + row * square_size
            rect = QRectF(x, y, 20, square_size)
            painter.drawText(rect, Qt.AlignCenter, char)

        # Draw Pieces from FEN
        if self.board_state:
            fen_rows = self.board_state.split(' ')[0].split('/')
            for row, fen_row in enumerate(fen_rows):
                col = 0
                for char in fen_row:
                    if char.isdigit():
                        col += int(char)
                    else:
                        x, y = get_xy(row, col)
                        self.draw_piece(painter, char, x, y, square_size)
                        col += 1
                        
        # Draw Best Move Arrow
        if self.best_move:
            try:
                src_sq = self.best_move[:2]
                dst_sq = self.best_move[2:4]
                src_r, src_c = get_rc(src_sq)
                dst_r, dst_c = get_rc(dst_sq)
                
                x1, y1 = get_xy(src_r, src_c)
                x2, y2 = get_xy(dst_r, dst_c)
                
                # Center of squares
                x1 += square_size / 2
                y1 += square_size / 2
                x2 += square_size / 2
                y2 += square_size / 2
                
                pen = QPen(QColor(0, 0, 255, 180), 4) # Blue transparent
                painter.setPen(pen)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                
                # Draw arrow head
                painter.setBrush(QBrush(QColor(0, 0, 255, 180)))
                # Simple circle at destination for now
                painter.drawEllipse(int(x2 - 5), int(y2 - 5), 10, 10)
                
            except Exception as e:
                print(f"Error drawing best move: {e}")

    def draw_piece(self, painter, char, x, y, size):
        # Unicode Chess Pieces
        # White: ♔♕♖♗♘♙
        # Black: ♚♛♜♝♞♟
        
        pieces = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }
        
        symbol = pieces.get(char, char)
        is_white = char.isupper()
        
        # Draw text
        # Use black for all because the symbols themselves are filled/outlined
        # But to make them pop on both squares:
        # White pieces (outline) -> White color with Black outline
        # Black pieces (filled) -> Black color
        
        font = painter.font()
        font.setPixelSize(int(size * 0.8)) # Larger size
        painter.setFont(font)
        
        text_rect = QRectF(x, y, size, size)
        
        if is_white:
            painter.setPen(QColor("white"))
            # Optional: Draw a shadow or outline if needed, but standard font rendering usually suffices
            # For better visibility on light squares, we might need a black outline effect, 
            # but QPainter.drawText doesn't support outline directly easily.
            # Instead, let's use a dark color for White pieces so they look like "White" pieces in a diagram (often white with black outline)
            # Actually, standard unicode '♔' is just an outline. If we draw it in Black, it looks like a white piece.
            # '♚' is filled. If we draw it in Black, it looks like a black piece.
            painter.setPen(QColor("black"))
        else:
            painter.setPen(QColor("black"))
            
        painter.drawText(text_rect, Qt.AlignCenter, symbol)

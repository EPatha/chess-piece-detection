import chess
import chess.pgn
import datetime

class StateManager:
    """
    Manages the internal chess game state using python-chess.
    Tracks moves, history, and validates legality.
    """
    def __init__(self):
        self.board = chess.Board()
        self.game_history = [] # List of moves
        self.start_time = datetime.datetime.now()

    def reset(self):
        """Resets the board to the initial starting position."""
        self.board.reset()
        self.game_history = []
        self.start_time = datetime.datetime.now()
        print("StateManager: Game reset.")

    def set_custom_position(self, fen):
        """Sets the board to a custom position and clears history."""
        self.board.set_fen(fen)
        self.game_history = []
        self.start_time = datetime.datetime.now()
        print(f"StateManager: Custom position set: {fen}")

    def make_move(self, uci_move):
        """
        Attempts to make a move on the internal board.
        Args:
            uci_move (str): Move in UCI format (e.g., "e2e4")
        Returns:
            bool: True if move was legal and made, False otherwise.
        """
        try:
            move = chess.Move.from_uci(uci_move)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.game_history.append(move)
                print(f"StateManager: Move {uci_move} made. FEN: {self.board.fen()}")
                return True
            else:
                print(f"StateManager: Illegal move {uci_move}")
                return False
        except ValueError:
            print(f"StateManager: Invalid UCI string {uci_move}")
            return False

    def undo_last_move(self):
        """
        Undoes the last move made on the board and removes it from game history.
        Returns:
            bool: True if a move was undone, False otherwise.
        """
        if len(self.board.move_stack) > 0:
            move = self.board.pop()
            # Unconditionally pop from history to ensure sync
            if self.game_history:
                self.game_history.pop()
            print(f"StateManager: Undid move {move.uci()}. FEN: {self.board.fen()}")
            return True
        return False

    def get_fen(self):
        return self.board.fen()

    def get_legal_moves(self):
        return [move.uci() for move in self.board.legal_moves]

    def is_game_over(self):
        return self.board.is_game_over()

    def get_pgn(self):
        try:
            game = chess.pgn.Game()
            game.headers["Event"] = "ChessMind Hybrid Game"
            game.headers["Site"] = "Local"
            game.headers["Date"] = self.start_time.strftime("%Y.%m.%d")
            game.headers["Round"] = "1"
            game.headers["White"] = "Player"
            game.headers["Black"] = "Player"
            
            # Determine starting position
            # Create a copy and pop all moves to get to the root state
            root_board = self.board.copy()
            while root_board.move_stack:
                root_board.pop()
            
            # Handle custom starting position
            if root_board.fen() != chess.STARTING_FEN:
                game.setup(root_board)
            
            node = game
            for move in self.game_history:
                node = node.add_variation(move)
                
            return str(game)
        except Exception as e:
            print(f"StateManager: Error generating PGN: {e}")
            return str(self.board.fen()) # Fallback to FEN

from PyQt5.QtCore import QObject, pyqtSignal
from .state_manager import StateManager
from .state_manager import StateManager
from .engine_manager import EngineManager
from .audio_manager import AudioManager
from .chess_clock import ChessClock
import chess

class HybridManager(QObject):
    """
    Central coordinator for the ChessMind Hybrid system.
    
    Integrates vision processing, game state management, engine analysis,
    and audio feedback. Handles the flow of information between the UI
    and the core logic components.
    """
    game_state_updated = pyqtSignal(str, str) # fen, last_move_uci
    log_message = pyqtSignal(str, str)
    evaluation_updated = pyqtSignal(str) # Re-emit from engine
    best_move_found = pyqtSignal(str) # Re-emit from engine
    illegal_move_attempted = pyqtSignal(str) # move_uci
    clock_updated = pyqtSignal(float, float) # white, black

    def __init__(self, game_mode_enabled=True):
        super().__init__()
        self.state_manager = StateManager()
        self.engine_manager = EngineManager()
        self.audio_manager = AudioManager()
        self.clock = ChessClock()
        self.clock.time_updated.connect(self.clock_updated)
        self.clock.flag_fall.connect(self.handle_flag_fall)
        
        self.ai_color = None # None, chess.WHITE, chess.BLACK
        self.game_mode_enabled = game_mode_enabled
        
        # Connect engine signals
        self.engine_manager.evaluation_updated.connect(self.evaluation_updated.emit)
        self.engine_manager.best_move_found.connect(self._on_best_move_found)
        
        if self.game_mode_enabled:
            self.engine_manager.start_engine()
        
        # Stability check variables
        self.current_stable_grid = None
        self.pending_grid = None
        self.stability_counter = 0
        self.STABILITY_THRESHOLD = 5 # Frames required to confirm a change
        self.is_processing = False
        
        # Initial board state (standard start)
        self.current_stable_grid = self._get_initial_grid()
        self.current_yolo_grid = None
        self.auto_sync_on_reset = False

    def update_yolo_state(self, grid):
        self.current_yolo_grid = grid

    def reset_game(self):
        """Resets the game state, clock, and engine analysis."""
        if self.auto_sync_on_reset and self.current_yolo_grid:
            self.log_message.emit("info", "Auto-syncing board from camera...")
            self.sync_board_from_camera()
        else:
            self.state_manager.reset()
            self.current_stable_grid = self._get_initial_grid()
            self.pending_grid = None
            self.stability_counter = 0
            self.game_state_updated.emit(self.state_manager.get_fen(), "")
            self.log_message.emit("info", "Game reset (Standard).")
            self.clock.start_game(600, 0) # Default 10 min
            
        self.is_processing = False
        if self.engine_manager.engine:
            self.engine_manager.stop_analysis()

    def sync_board_from_camera(self):
        """
        Sets the internal game state based on the current YOLO detections.
        """
        if not self.current_yolo_grid:
            self.log_message.emit("warning", "No YOLO data available to sync.")
            return

        board = chess.Board(None) # Empty board
        board.clear()
        
        # Map YOLO classes to chess.Piece
        # YOLO: 'white-rook' -> chess.Piece(chess.ROOK, chess.WHITE)
        piece_map = {
            'white-pawn': chess.PAWN, 'white-rook': chess.ROOK, 'white-knight': chess.KNIGHT,
            'white-bishop': chess.BISHOP, 'white-queen': chess.QUEEN, 'white-king': chess.KING,
            'black-pawn': chess.PAWN, 'black-rook': chess.ROOK, 'black-knight': chess.KNIGHT,
            'black-bishop': chess.BISHOP, 'black-queen': chess.QUEEN, 'black-king': chess.KING
        }
        
        for row in range(8):
            for col in range(8):
                yolo_class = self.current_yolo_grid[row][col]
                if yolo_class:
                    piece_type = piece_map.get(yolo_class)
                    if piece_type:
                        color = chess.WHITE if 'white' in yolo_class else chess.BLACK
                        # chess.square(file_index, rank_index)
                        # file: 0=a (col), rank: 0=1 (7-row)
                        sq = chess.square(col, 7 - row)
                        board.set_piece_at(sq, chess.Piece(piece_type, color))
        
        # Set turn (default to White, or maybe infer? Inferring turn is hard visually)
        # We will assume White to move unless user changes it manually later
        board.turn = chess.WHITE
        
        # Update StateManager
        self.state_manager.set_custom_position(board.fen())
        
        # Update Visual Grid (for change detection)
        # We need to convert the new board state back to 'white'/'black'/'empty' grid
        self.current_stable_grid = self._fen_to_grid(board.fen())
        self.pending_grid = None
        self.stability_counter = 0
        
        self.game_state_updated.emit(board.fen(), "")
        self.log_message.emit("success", "Board synced from camera.")
        
        # Reset Clock
        self.clock.start_game(600, 0)

    def _get_initial_grid(self):
        """Returns the initial 8x8 visual grid for a standard chess game."""
        # Returns 8x8 grid of 'white', 'black', 'empty' for standard start
        grid = [['empty'] * 8 for _ in range(8)]
        # Black pieces
        grid[0] = ['black'] * 8
        grid[1] = ['black'] * 8
        # White pieces
        grid[6] = ['white'] * 8
        grid[7] = ['white'] * 8
        return grid

    def reset_game(self):
        """Resets the game state, clock, and engine analysis."""
        self.state_manager.reset()
        self.current_stable_grid = self._get_initial_grid()
        self.pending_grid = None
        self.stability_counter = 0
        self.is_processing = False
        self.game_state_updated.emit(self.state_manager.get_fen(), "")
        self.log_message.emit("info", "Game reset.")
        self.clock.start_game(600, 0) # Default 10 min
        if self.engine_manager.engine:
            self.engine_manager.stop_analysis()

    def handle_flag_fall(self, is_white):
        """Handles the event when a player's clock runs out of time."""
        loser = "White" if is_white else "Black"
        self.log_message.emit("warning", f"Time's up! {loser} lost on time.")
        self.audio_manager.speak(f"{loser} lost on time")

    def apply_manual_correction(self, fen):
        """
        Manually sets the game state to a specific FEN string.
        Useful for correcting desynchronization between the physical board and internal state.
        """
        self.state_manager.set_custom_position(fen)
        # We also need to update the visual grid to match the new FEN
        # This is tricky because visual grid is just colors.
        # We can approximate it from the FEN.
        self.current_stable_grid = self._fen_to_grid(fen)
        self.pending_grid = None
        self.stability_counter = 0
        
        self.game_state_updated.emit(fen, "")
        self.log_message.emit("warning", "Manual correction applied.")
        
        if self.engine_manager.engine:
            self.engine_manager.analyze_position(fen)

    def _fen_to_grid(self, fen):
        """Converts a FEN string to an 8x8 visual grid of colors."""
        board = chess.Board(fen)
        grid = [['empty'] * 8 for _ in range(8)]
        for rank in range(8):
            for file in range(8):
                piece = board.piece_at(chess.square(file, 7-rank)) # Rank 0 is bottom (row 7)
                if piece:
                    grid[rank][file] = 'white' if piece.color == chess.WHITE else 'black'
        return grid

    def update_board_state(self, visual_grid):
        """
        Receives a new visual grid from the ProcessingThread.
        Checks for stability and infers moves if the board state changes.
        """
        # Throttled debug logging
        if not hasattr(self, '_debug_frame_count'):
            self._debug_frame_count = 0
        self._debug_frame_count += 1
        
        if self._debug_frame_count % 60 == 0:
            self.log_message.emit("debug", f"HybridManager: Processing={self.is_processing}, Stable={self.stability_counter}/{self.STABILITY_THRESHOLD}")

        if self.is_processing:
            return

        if self.current_stable_grid is None:
            self.current_stable_grid = visual_grid
            return

        # Check if visual_grid matches pending_grid
        if self.pending_grid == visual_grid:
            self.stability_counter += 1
        else:
            self.pending_grid = visual_grid
            self.stability_counter = 0

        # If stable enough, process the change
        if self.stability_counter >= self.STABILITY_THRESHOLD:
            if self.pending_grid != self.current_stable_grid:
                self.log_message.emit("debug", "Stable board change detected. Inferring move...")
                self.is_processing = True
                try:
                    self._process_change(self.pending_grid)
                finally:
                    self.current_stable_grid = self.pending_grid
                    self.is_processing = False
            
            # Reset counter to avoid repeated processing (though != check handles it)
            # self.stability_counter = 0 

    def _process_change(self, new_grid):
        """Infers and executes a move based on the difference between old and new grids."""
        move_uci = self._infer_move(self.current_stable_grid, new_grid)
        
        if move_uci:
            self.log_message.emit("info", f"Inferred Move: {move_uci}")
            if self.state_manager.make_move(move_uci):
                self.game_state_updated.emit(self.state_manager.get_fen(), move_uci)
                self.log_message.emit("success", f"Move {move_uci} confirmed.")
                
                # Audio Announcement
                self.audio_manager.announce_move(move_uci)
                
                # Switch Clock
                self.clock.switch_turn()
                
                if self.state_manager.board.is_checkmate():
                    self.audio_manager.announce_checkmate()
                    self.clock.stop()
                elif self.state_manager.board.is_check():
                    self.audio_manager.announce_check()
                elif self.state_manager.board.is_game_over():
                    self.clock.stop()
                
                # Trigger analysis if enabled or AI turn
                if self.engine_manager.engine:
                    # Always analyze if engine is on, to update eval bar
                    self.engine_manager.analyze_position(self.state_manager.get_fen())
            else:
                self.log_message.emit("warning", f"Illegal move inferred: {move_uci}")
                self.audio_manager.announce_illegal_move()
        else:
            self.log_message.emit("debug", "Board changed but no clear move inferred.")

    def undo_last_move(self):
        """Undoes the last move and updates the game state."""
        if self.state_manager.undo_last_move():
            # Get the new last move (if any)
            last_move = ""
            if len(self.state_manager.board.move_stack) > 0:
                last_move = self.state_manager.board.peek().uci()
            
            self.game_state_updated.emit(self.state_manager.get_fen(), last_move)
            self.log_message.emit("info", "Last move undone.")
            
            # Re-analyze
            if self.engine_manager.engine:
                self.engine_manager.analyze_position(self.state_manager.get_fen())
        else:
            self.log_message.emit("warning", "No moves to undo.")

    def _infer_move(self, old_grid, new_grid):
        """
        Compare old and new grids to find the move.
        Simple logic:
        - 1 square became empty (Source)
        - 1 square became occupied (Target) OR changed color (Capture)
        """
        diffs = []
        for r in range(8):
            for c in range(8):
                if old_grid[r][c] != new_grid[r][c]:
                    diffs.append(((r, c), old_grid[r][c], new_grid[r][c]))
        
        if not diffs:
            return None

        # Analyze diffs
        # Standard Move: 2 diffs. Source (Piece -> Empty), Target (Empty/Piece -> Piece)
        src = None
        dst = None
        
        # Heuristic:
        # Source: Was occupied, Now empty
        # Target: Was empty (or occupied by opponent), Now occupied by same color as Source was
        
        potential_srcs = []
        potential_dsts = []
        
        for pos, old_val, new_val in diffs:
            if new_val == 'empty' and old_val != 'empty':
                potential_srcs.append((pos, old_val))
            elif new_val != 'empty':
                potential_dsts.append((pos, new_val))
                
        if len(potential_srcs) == 1 and len(potential_dsts) == 1:
            src_pos, src_color = potential_srcs[0]
            dst_pos, dst_color = potential_dsts[0]
            
            # Check color consistency (piece moving should be same color)
            if src_color == dst_color:
                # Validate against current turn
                current_turn_color = 'white' if self.state_manager.board.turn == chess.WHITE else 'black'
                if src_color != current_turn_color:
                    self.log_message.emit("warning", f"Wrong turn: Detected {src_color} move, but it's {current_turn_color}'s turn.")
                    return None

                src_sq = chess.square_name(chess.square(src_pos[1], 7 - src_pos[0]))
                dst_sq = chess.square_name(chess.square(dst_pos[1], 7 - dst_pos[0]))
                
                move_uci = src_sq + dst_sq
                
                # Check for promotion
                # If piece is a pawn and reaches rank 8 (row 0 for white) or rank 1 (row 7 for black)
                # We need to know WHAT piece moved.
                # We can check the board state from StateManager to see what piece is at src_sq
                # But StateManager has the OLD state before this move.
                
                piece = self.state_manager.board.piece_at(chess.square(src_pos[1], 7 - src_pos[0]))
                if piece and piece.piece_type == chess.PAWN:
                    # Check if pawn reached the last rank
                    is_promotion = False
                    if piece.color == chess.WHITE and dst_pos[0] == 0:
                        is_promotion = True
                    elif piece.color == chess.BLACK and dst_pos[0] == 7:
                        is_promotion = True
                        
                    if is_promotion:
                        if hasattr(self, 'promotion_callback') and self.promotion_callback:
                            promo_char = self.promotion_callback()
                            move_uci += promo_char
                        else:
                            move_uci += 'q' # Default to Queen
                
                return move_uci
        
        # Castling (King moves 2 squares, Rook moves) - 4 diffs
        # En Passant - 3 diffs (Pawn moves, Pawn captured elsewhere)
        # For MVP, let's stick to simple moves first. 
        # If complex, maybe we can rely on python-chess to validate all legal moves 
        # and see which one matches the state change?
        
        return None

    def set_ai_mode(self, mode):
        """Sets the game mode (PvP or PvAI)."""
        # mode: "PvP", "PvAI_W" (User is White), "PvAI_B" (User is Black)
        if mode == "PvP":
            self.ai_color = None
            self.log_message.emit("info", "Mode: Human vs Human")
            self.toggle_analysis(False)
        elif mode == "PvAI_W":
            self.ai_color = chess.BLACK
            self.log_message.emit("info", "Mode: Human (White) vs AI (Black)")
            self.toggle_analysis(True)
        elif mode == "PvAI_B":
            self.ai_color = chess.WHITE
            self.log_message.emit("info", "Mode: Human (Black) vs AI (White)")
            self.toggle_analysis(True)
            
        # Trigger check if it's already AI's turn
        if self.ai_color is not None and self.state_manager.board.turn == self.ai_color:
             self.engine_manager.analyze_position(self.state_manager.get_fen())

    def _on_best_move_found(self, move_uci):
        """Callback when the engine finds the best move."""
        self.best_move_found.emit(move_uci)
        
        # If it's AI's turn, announce it
        if self.ai_color is not None and self.state_manager.board.turn == self.ai_color:
            self.log_message.emit("info", f"🤖 AI Suggests: {move_uci}")

    def toggle_analysis(self, enabled):
        """Starts or stops the Stockfish engine analysis."""
        if enabled:
            if not self.game_mode_enabled:
                self.log_message.emit("warning", "Game Mode (Engine) is disabled in config.")
                return

            if self.engine_manager.start_engine():
                self.log_message.emit("success", "Stockfish Engine Started.")
                # Analyze current position
                self.engine_manager.analyze_position(self.state_manager.get_fen())
            else:
                self.log_message.emit("error", "Failed to start Stockfish. Is it installed?")
        else:
            self.engine_manager.stop_engine()
            self.log_message.emit("info", "Stockfish Engine Stopped.")

    def get_pgn(self):
        """Returns the current game PGN string."""
        return self.state_manager.get_pgn()

    def update_stability_threshold(self, value):
        """Updates the number of stable frames required to confirm a board change."""
        self.STABILITY_THRESHOLD = value
        self.log_message.emit("info", f"Stability Threshold set to {value} frames")

"""Chess logic and game state management."""
import chess
import chess.pgn
import time
import datetime


class OccupancyChessSystem:
    """Chess game state manager using occupancy-based move detection."""
    
    def __init__(self, debounce_time=1.5):
        self.board = chess.Board()
        self.debounce_time = debounce_time
        self.stable_start_time = 0
        self.last_occupancy_grid = None
        self.expected_occupancy = self._get_board_occupancy(self.board)
        self.last_move = None  # Track last move for visualization
        self.move_list = []  # Track Move objects for PGN export

    def sync_board(self, visual_occupancy_grid):
        """Initialize board from visual setup (standard starting position assumed)."""
        log_msgs = []
        log_msgs.append("Syncing internal board to standard starting position...")
        
        # Reset to standard starting position
        self.board = chess.Board()
        
        self.expected_occupancy = self._get_board_occupancy(self.board)
        self.last_occupancy_grid = visual_occupancy_grid
        log_msgs.append("Board Sync Complete. Assuming standard starting position.")
        return log_msgs

    def undo_last_move(self):
        """Undo the most recent move if possible."""
        if not self.move_list:
            return False
        # Pop last move from board
        try:
            self.board.pop()
        except IndexError:
            # No move to pop
            return False
        # Remove from move list
        self.move_list.pop()
        # Update last_move
        if self.move_list:
            self.last_move = self.move_list[-1]
        else:
            self.last_move = None
        return True

    def _get_board_occupancy(self, board):
        """Convert chess board to occupancy grid."""
        grid = [[False]*8 for _ in range(8)]
        for r in range(8):
            for c in range(8):
                rank = 7 - r
                file = c
                square = chess.square(file, rank)
                if board.piece_at(square) is not None:
                    grid[r][c] = True
        return grid

    def update(self, detected_occupancy_grid, debug_mode=False, no_turn_mode=False):
        """Update game state based on detected occupancy."""
        current_time = time.time()
        if self.last_occupancy_grid is None:
            self.last_occupancy_grid = detected_occupancy_grid
            self.stable_start_time = current_time
            return None, []

        logs = []
        if detected_occupancy_grid == self.last_occupancy_grid:
            if current_time - self.stable_start_time > self.debounce_time:
                expected = self._get_board_occupancy(self.board)
                if detected_occupancy_grid != expected:
                    logs.append(f"DEBUG: Stable State Differs. Expected {sum([sum(r) for r in expected])}, Got {sum([sum(r) for r in detected_occupancy_grid])}")
                    
                    move = self._infer_move(expected, detected_occupancy_grid, logs, debug_mode)
                    
                    if move:
                        # Check No Turn Mode
                        if no_turn_mode and not debug_mode:
                            piece = self.board.piece_at(move.from_square)
                            if piece and piece.color != self.board.turn:
                                logs.append(f"No Turn Mode: Switching turn to {'White' if piece.color else 'Black'}")
                                self.board.turn = piece.color
                        
                        san = "Move"
                        if not debug_mode:
                            if move in self.board.legal_moves:
                                try:
                                    san = self.board.san(move)
                                    self.board.push(move)
                                    self.last_move = move  # Track last move
                                    self.move_list.append(move)  # Store Move object
                                except:
                                    san = move.uci()
                                    self.board.push(move)
                                    self.last_move = move
                                    self.move_list.append(san)
                                self.stable_start_time = current_time 
                                return san, logs
                            else:
                                logs.append(f"Illegal Move Detected: {move.uci()}")
                                from utils.audio import speak
                                speak("Illegal Move")
                                self.stable_start_time = current_time
                                return None, logs
                        else:
                            # Debug mode: Force the move
                            san = f"Force {move.uci()}"
                            piece = self.board.remove_piece_at(move.from_square)
                            if piece:
                                self.board.set_piece_at(move.to_square, piece)
                            else:
                                logs.append("DEBUG: Tried to move non-existent piece!")

                            self.stable_start_time = current_time 
                            return san, logs
                    else:
                        # Diff logging
                        diffs = []
                        for r in range(8):
                            for c in range(8):
                                if expected[r][c] != detected_occupancy_grid[r][c]:
                                    rank = 7 - r
                                    file = c
                                    sq_name = chess.square_name(chess.square(file, rank))
                                    state = "Occ" if detected_occupancy_grid[r][c] else "Emp"
                                    exp = "Occ" if expected[r][c] else "Emp"
                                    diffs.append(f"{sq_name}: {exp}->{state}")
                        if diffs:
                            logs.append(f"DEBUG: Diffs: {', '.join(diffs)}")
                        
                        self.stable_start_time = current_time
        else:
            self.last_occupancy_grid = detected_occupancy_grid
            self.stable_start_time = current_time
            
        return None, logs

    def _infer_move(self, expected_grid, visual_grid, logs, debug_mode=False):
        """Infer chess move from occupancy grid changes."""
        sources = []
        targets = []
        for r in range(8):
            for c in range(8):
                was_occ = expected_grid[r][c]
                is_occ = visual_grid[r][c]
                if was_occ and not is_occ:
                    sources.append((r, c))
                elif not was_occ and is_occ:
                    targets.append((r, c))
                    
        def to_square(r, c):
            return chess.square(c, 7 - r)

        # Case 1: Standard Move (1 Source, 1 Target)
        if len(sources) == 1 and len(targets) == 1:
            src = to_square(*sources[0])
            dst = to_square(*targets[0])
            move = chess.Move(src, dst)
            
            if debug_mode:
                return move 

            # Check for promotion
            if self.board.piece_at(src) and self.board.piece_at(src).piece_type == chess.PAWN:
                if chess.square_rank(dst) in [0, 7]:
                    move = chess.Move(src, dst, promotion=chess.QUEEN)
            
            return move
                
        # Case 2: Capture (1 Source, 0 Targets)
        # Visually: Source becomes empty, Target remains occupied (so no change in target state)
        elif len(sources) == 1 and len(targets) == 0:
            src = to_square(*sources[0])
            if debug_mode:
                logs.append("DEBUG: Capture detected (Source disappeared). Target unknown in Debug Mode.")
                return None

            # Find legal moves from this source that are captures
            candidates = []
            for m in self.board.legal_moves:
                if m.from_square == src and self.board.is_capture(m):
                    # For a capture, the destination must be occupied in the expected grid
                    # (unless en passant, which is handled separately or treated as capture)
                    # We verify that the visual grid shows the destination as OCCUPIED (which it should, as it was before)
                    dst_r = 7 - chess.square_rank(m.to_square)
                    dst_c = chess.square_file(m.to_square)
                    if visual_grid[dst_r][dst_c]:
                        candidates.append(m)
            
            if len(candidates) == 1:
                move = candidates[0]
                # Check for promotion on capture
                if self.board.piece_at(src).piece_type == chess.PAWN and chess.square_rank(move.to_square) in [0, 7]:
                    move.promotion = chess.QUEEN
                return move
            elif len(candidates) > 1:
                # Ambiguity Resolution: Material Gain Heuristic
                # Choose the move that captures the highest value piece
                best_move = None
                max_val = -1
                
                piece_values = {
                    chess.QUEEN: 9, chess.ROOK: 5, chess.BISHOP: 3, chess.KNIGHT: 3, chess.PAWN: 1
                }
                
                logs.append(f"Ambiguous capture from {chess.square_name(src)}. Candidates: {[m.uci() for m in candidates]}")
                
                for m in candidates:
                    captured_piece = self.board.piece_at(m.to_square)
                    val = 0
                    if captured_piece:
                        val = piece_values.get(captured_piece.piece_type, 0)
                    
                    if val > max_val:
                        max_val = val
                        best_move = m
                
                if best_move:
                    logs.append(f"Resolved ambiguity: Choosing {best_move.uci()} (Captures value {max_val})")
                    # Check for promotion on resolved capture
                    if self.board.piece_at(src).piece_type == chess.PAWN and chess.square_rank(best_move.to_square) in [0, 7]:
                        best_move.promotion = chess.QUEEN
                    return best_move
                else:
                    return None

        # Case 3: Castling (2 Sources, 2 Targets)
        elif len(sources) == 2 and len(targets) == 2:
            for move in self.board.legal_moves:
                if self.board.is_castling(move):
                    self.board.push(move)
                    temp_occ = self._get_board_occupancy(self.board)
                    self.board.pop()
                    if temp_occ == visual_grid:
                        return move

        # Case 4: En Passant (2 Sources, 1 Target)
        # Pawn moves to empty square (Target), but captures piece on another square (2nd Source)
        elif len(sources) == 2 and len(targets) == 1:
             for move in self.board.legal_moves:
                if self.board.is_en_passant(move):
                    self.board.push(move)
                    temp_occ = self._get_board_occupancy(self.board)
                    self.board.pop()
                    if temp_occ == visual_grid:
                        return move
        return None

    def export_pgn(self, filename=None):
        """Export game to PGN format."""
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.pgn"
        
        game = chess.pgn.Game()
        game.headers["Event"] = "BlindChess Vision Game"
        game.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = "Player"
        game.headers["Black"] = "Player"
        
        node = game
        for move in self.move_list:
            if move:
                node = node.add_variation(move)
        
        with open(filename, 'w') as f:
            f.write(str(game))
        
        return filename

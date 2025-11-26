import chess
import time

class OccupancyChessSystem:
    def __init__(self, debounce_time=1.5):
        self.board = chess.Board()
        self.debounce_time = debounce_time
        self.stable_start_time = 0
        self.last_occupancy_grid = None
        self.current_occupancy_grid = None
        
        # Initialize expected occupancy from the starting board
        self.expected_occupancy = self._get_board_occupancy(self.board)

    def _get_board_occupancy(self, board):
        """Returns 8x8 boolean grid of occupancy based on a python-chess board"""
        grid = [[False for _ in range(8)] for _ in range(8)]
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # chess.SQUARES goes a1, b1... h8. 
                # We need to map to our 8x8 grid where row 0 is Rank 8 (top), col 0 is File A.
                # Rank: chess.square_rank(square) -> 0-7 (0 is Rank 1). We want 0 to be Rank 8.
                # File: chess.square_file(square) -> 0-7 (0 is File A).
                
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                
                # Map to visual grid (row 0 = Rank 8)
                row = 7 - rank
                col = file
                grid[row][col] = True
        return grid

    def update(self, detected_occupancy_grid):
        """
        Updates the system with the latest visual occupancy grid.
        Returns the move SAN string if a move is confirmed, else None.
        """
        current_time = time.time()
        
        # If this is the first frame, just initialize
        if self.last_occupancy_grid is None:
            self.last_occupancy_grid = detected_occupancy_grid
            self.stable_start_time = current_time
            return None

        # Check if the visual grid is stable (hasn't changed from last frame)
        if detected_occupancy_grid == self.last_occupancy_grid:
            # It is stable. Check if it has been stable long enough.
            if current_time - self.stable_start_time > self.debounce_time:
                # It's a stable new state.
                expected = self._get_board_occupancy(self.board)
                
                # Debug: Print if we are stable but state doesn't match expected
                if detected_occupancy_grid != expected:
                    print(f"DEBUG: Stable State Differs. Expected {sum([sum(r) for r in expected])} pieces, Got {sum([sum(r) for r in detected_occupancy_grid])}")
                    move = self._infer_move(expected, detected_occupancy_grid)
                    if move:
                        # Move confirmed and valid
                        self.board.push(move)
                        self.stable_start_time = current_time 
                        return self.board.san(move) # Return SAN for speech
                    else:
                        # Could not infer a valid move. 
                        print("DEBUG: No legal move found for this state change.")
                        # Print the difference
                        # for r in range(8):
                        #     print(f"Row {r}: Exp {expected[r]} vs Got {detected_occupancy_grid[r]}")
                        pass
        else:
            # The grid changed (unstable). Reset timer.
            # print("DEBUG: Grid unstable (change detected)")
            self.last_occupancy_grid = detected_occupancy_grid
            self.stable_start_time = current_time
            
        return None

    def _infer_move(self, expected_grid, visual_grid):
        """
        Compare expected vs visual grids to find the move.
        Logic:
        - Source square: Was Occupied (True) -> Now Empty (False)
        - Target square: Was Empty/Occupied -> Now Occupied (True) [and different from expected if capture]
        
        This is tricky because:
        - Simple move: 1 source (True->False), 1 target (False->True).
        - Capture: 1 source (True->False), 1 target (True->True but piece changed... wait, we only see occupancy).
          For capture, the target square is Occupied in Expected AND Occupied in Visual.
          So purely by occupancy, a capture looks like: Source disappears. Target stays occupied.
          
          Wait, if I capture a piece:
          - I pick up my piece (Source becomes Empty).
          - I remove opponent piece (Target becomes Empty... momentarily).
          - I place my piece on Target (Target becomes Occupied).
          
          So the final stable state is:
          - Source: Empty (was Occupied)
          - Target: Occupied (was Occupied)
          
          So for a capture, the ONLY difference in occupancy is the Source square becoming empty!
          The Target square remains occupied (different piece, but we don't know that).
          
          This is ambiguous. If only one square changes from Occupied to Empty, it could be a capture.
          But which square is the target? We don't know the target from occupancy change alone if it was a capture.
          
          UNLESS we check all legal moves.
          If we see Source -> Empty.
          We check all legal moves from Source.
          If there is only one legal capture from Source, we might guess it.
          But if there are multiple captures, or a capture and a non-capture (to an already occupied square? No, non-capture is to empty).
          
          Let's refine:
          - Move to Empty: Source (O->E), Target (E->O). 2 changes.
          - Capture: Source (O->E), Target (O->O). 1 change (Source).
          
          So:
          1. Identify all squares that changed from Occupied to Empty (Potential Sources).
          2. Identify all squares that changed from Empty to Occupied (Potential Targets).
          
          Case A: 1 Source, 1 Target.
          - Likely a normal move. Check if Source->Target is legal.
          
          Case B: 1 Source, 0 Targets.
          - Likely a capture. The target was already occupied.
          - We check all legal moves from Source that land on an *occupied* square.
          - If there is only one such move, we execute it.
          - If multiple, we can't be sure (ambiguous).
          
          Case C: Castling.
          - King moves 2 squares. Rook jumps.
          - King Source (O->E), King Target (E->O).
          - Rook Source (O->E), Rook Target (E->O).
          - 2 Sources, 2 Targets.
          
          Case D: En Passant.
          - Pawn moves diagonal to empty square. Captured pawn (behind) disappears.
          - Source (O->E).
          - Target (E->O).
          - Captured Square (O->E).
          - 2 Sources, 1 Target.
        """
        
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
                    
        # Helper to convert (row, col) to chess.Square
        def to_square(r, c):
            # row 0 = Rank 8, col 0 = File A
            rank = 7 - r
            file = c
            return chess.square(file, rank)

        # Case A: 1 Source, 1 Target (Normal Move)
        if len(sources) == 1 and len(targets) == 1:
            src = to_square(*sources[0])
            dst = to_square(*targets[0])
            move = chess.Move(src, dst)
            
            # Check promotion (auto-promote to Queen for simplicity)
            if self.board.piece_at(src) and self.board.piece_at(src).piece_type == chess.PAWN:
                if chess.square_rank(dst) in [0, 7]:
                    move = chess.Move(src, dst, promotion=chess.QUEEN)
            
            if move in self.board.legal_moves:
                return move
                
        # Case B: 1 Source, 0 Targets (Capture)
        elif len(sources) == 1 and len(targets) == 0:
            src = to_square(*sources[0])
            # Find legal moves from src that are captures
            candidates = []
            for move in self.board.legal_moves:
                if move.from_square == src:
                    if self.board.is_capture(move):
                        candidates.append(move)
            
            if len(candidates) == 1:
                return candidates[0]
            elif len(candidates) > 1:
                print(f"Ambiguous capture from {chess.square_name(src)}")
                # Heuristic: Maybe we can't distinguish. 
                # But wait, if we have multiple captures from the same piece, we are stuck.
                # However, usually there's only one valid capture per piece in a specific direction? 
                # No, a Queen can capture multiple pieces.
                pass

        # Case C: Castling (2 Sources, 2 Targets)
        elif len(sources) == 2 and len(targets) == 2:
            # Check if any legal move matches this pattern
            # Castling involves King and Rook.
            for move in self.board.legal_moves:
                if self.board.is_castling(move):
                    # Simulate castling to see occupancy changes
                    self.board.push(move)
                    temp_occ = self._get_board_occupancy(self.board)
                    self.board.pop()
                    
                    # Check if temp_occ matches visual_grid
                    if temp_occ == visual_grid:
                        return move

        # Case D: En Passant (2 Sources, 1 Target)
        elif len(sources) == 2 and len(targets) == 1:
             for move in self.board.legal_moves:
                if self.board.is_en_passant(move):
                    self.board.push(move)
                    temp_occ = self._get_board_occupancy(self.board)
                    self.board.pop()
                    if temp_occ == visual_grid:
                        return move
                        
        return None

import chess
import chess.engine
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class EngineManager(QObject):
    evaluation_updated = pyqtSignal(str) # e.g. "+1.5", "M4"
    best_move_found = pyqtSignal(str) # UCI move
    engine_status = pyqtSignal(bool) # True if running

    def __init__(self, engine_path="stockfish"):
        super().__init__()
        self.engine_path = engine_path
        self.engine = None
        self.analysis_limit = chess.engine.Limit(time=1.0) # 1 second per move

    def start_engine(self):
        try:
            # Try to find stockfish in common locations if default fails
            paths = [self.engine_path, "/opt/homebrew/bin/stockfish", "/usr/local/bin/stockfish"]
            
            for path in paths:
                try:
                    self.engine = chess.engine.SimpleEngine.popen_uci(path)
                    print(f"EngineManager: Started Stockfish at {path}")
                    self.engine_status.emit(True)
                    return True
                except FileNotFoundError:
                    continue
            
            print("EngineManager: Stockfish not found.")
            self.engine_status.emit(False)
            return False
        except Exception as e:
            print(f"EngineManager: Error starting engine: {e}")
            self.engine_status.emit(False)
            return False

    def stop_engine(self):
        if self.engine:
            self.engine.quit()
            self.engine = None
            self.engine_status.emit(False)
            print("EngineManager: Engine stopped.")

    def analyze_position(self, fen):
        if not self.engine:
            return

        board = chess.Board(fen)
        try:
            info = self.engine.analyse(board, self.analysis_limit)
            
            # Parse score
            score = info["score"].white()
            if score.is_mate():
                score_str = f"M{score.mate()}"
            else:
                score_str = f"{score.score() / 100.0:+.2f}"
            
            self.evaluation_updated.emit(score_str)
            
            # Best move
            if "pv" in info:
                best_move = info["pv"][0]
                self.best_move_found.emit(best_move.uci())
                
        except Exception as e:
            print(f"EngineManager: Analysis failed: {e}")

    def get_best_move(self, fen):
        if not self.engine:
            return None
        
        board = chess.Board(fen)
        result = self.engine.play(board, self.analysis_limit)
        return result.move.uci() if result.move else None

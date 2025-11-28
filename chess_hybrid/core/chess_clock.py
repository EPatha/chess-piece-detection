from PyQt5.QtCore import QObject, QTimer, pyqtSignal
import time
import chess

class ChessClock(QObject):
    time_updated = pyqtSignal(float, float) # white_time, black_time
    flag_fall = pyqtSignal(bool) # True if White ran out, False if Black

    def __init__(self, initial_time=600, increment=0):
        super().__init__()
        self.white_time = initial_time
        self.black_time = initial_time
        self.increment = increment
        self.active_color = None # chess.WHITE or chess.BLACK
        self.last_update = None
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.setInterval(100) # Update every 100ms

    def start_game(self, initial_time=600, increment=0):
        self.white_time = initial_time
        self.black_time = initial_time
        self.increment = increment
        self.active_color = chess.WHITE
        self.last_update = time.time()
        self.timer.start()
        self.time_updated.emit(self.white_time, self.black_time)

    def stop(self):
        self.timer.stop()
        self.active_color = None

    def switch_turn(self):
        if self.active_color is None: return
        
        # Apply increment to the side that just finished
        if self.active_color == chess.WHITE:
            self.white_time += self.increment
            self.active_color = chess.BLACK
        else:
            self.black_time += self.increment
            self.active_color = chess.WHITE
            
        self.last_update = time.time()
        self.time_updated.emit(self.white_time, self.black_time)

    def _update_time(self):
        if self.active_color is None: return
        
        now = time.time()
        delta = now - self.last_update
        self.last_update = now
        
        if self.active_color == chess.WHITE:
            self.white_time -= delta
            if self.white_time <= 0:
                self.white_time = 0
                self.stop()
                self.flag_fall.emit(True)
        else:
            self.black_time -= delta
            if self.black_time <= 0:
                self.black_time = 0
                self.stop()
                self.flag_fall.emit(False)
                
        self.time_updated.emit(self.white_time, self.black_time)

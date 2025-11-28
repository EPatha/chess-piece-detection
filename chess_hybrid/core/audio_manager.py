from PyQt5.QtCore import QObject
from PyQt5.QtTextToSpeech import QTextToSpeech

class AudioManager(QObject):
    def __init__(self):
        super().__init__()
        self.tts = QTextToSpeech()
        
        # Optional: Set locale or voice if needed
        # available_locales = self.tts.availableLocales()
        # if available_locales:
        #     self.tts.setLocale(available_locales[0])
            
    def announce_move(self, move_uci):
        # Convert UCI (e.g., e2e4) to spoken text (e.g., "e2 to e4")
        text = f"{move_uci[:2]} to {move_uci[2:]}"
        self.speak(text)

    def announce_check(self):
        self.speak("Check")
        
    def announce_checkmate(self):
        self.speak("Checkmate")

    def announce_illegal_move(self):
        self.speak("Illegal move")

    def speak(self, text):
        # QTextToSpeech is non-blocking and handles its own queue/threading
        self.tts.say(text)

"""Audio utility functions."""
import pyttsx3

_engine = None

def speak(text):
    """Speak the given text using text-to-speech."""
    global _engine
    try:
        if _engine is None:
            _engine = pyttsx3.init()
        _engine.say(text)
        _engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

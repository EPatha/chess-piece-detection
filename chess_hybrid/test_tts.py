from PyQt5.QtCore import QCoreApplication
try:
    from PyQt5.QtTextToSpeech import QTextToSpeech
    print("QTextToSpeech imported successfully")
    app = QCoreApplication([])
    tts = QTextToSpeech()
    available_engines = tts.availableEngines()
    print(f"Available Engines: {available_engines}")
    if available_engines:
        print("TTS Engine available")
    else:
        print("No TTS Engine available")
except ImportError:
    print("QTextToSpeech import failed")
except Exception as e:
    print(f"Error: {e}")

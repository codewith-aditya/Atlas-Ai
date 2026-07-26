# auto_start.py  (NEW FILE)
# This file will auto-speak & auto-start the mic after Atlas UI is ready

from PyQt5.QtCore import QTimer

def enable_auto_start(ui, listener, speak, welcome_message):
    """
    Automatically:
    1. Speak Boot Message
    2. Start Listening/Mic
    """

    # Welcome message
    def delayed_speak():
        speak(welcome_message)
        print("[Auto-Start] Welcome message spoken.")

    # Auto boot & mic
    QTimer.singleShot(1000, delayed_speak)
    QTimer.singleShot(2000, lambda: speak("Atlas is now online and listening."))
    QTimer.singleShot(2500, listener.start_listening)  # Auto Mic start

    print("[Auto-Start] Auto-start enabled successfully.")

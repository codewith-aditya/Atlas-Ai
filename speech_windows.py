"""
Atlas TTS Engine
Primary: Windows PowerShell SAPI (Microsoft David)
Optional: tts-1-hd API available via speak_premium()
"""

import logging
import threading
import re
import subprocess
import tempfile
import os
import time

# Initialize speaking state
is_speaking = threading.Event()

# ============================================================================
# OPTIONAL: Premium TTS API Configuration (use speak_premium() to call)
# ============================================================================
TTS_API_URL = "http://3.90.176.251:8000/v1/audio/speech"
TTS_MODEL = "tts-1-hd"
TTS_VOICE = "ballad"  # British male, JARVIS-style
TEMP_DIR = tempfile.gettempdir()


def remove_emojis(text):
    """Remove emojis and other non-text characters from the given text."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F1E0-\U0001F1FF"  # Flags
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA70-\U0001FAFF"  # Symbols & Pictographs Extended-A
        "\U00002500-\U00002BEF"  # Box Drawing and Misc Symbols
        "\U0001F018-\U0001F270"  # More Misc Symbols
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)


def speak_thread_func(text):
    """Worker function for speaking using Microsoft David"""
    is_speaking.set()
    logging.info("is_speaking set to True")
    print(f"[Speech] Speaking: {text[:50]}...")

    try:
        # Escape quotes for PowerShell
        escaped_text = text.replace('"', '`"').replace("'", "''")
        
        # Use Windows PowerShell SAPI for TTS
        ps_command = f'''
Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speak.Rate = 1
$speak.Speak("{escaped_text}")
'''
        
        # Run PowerShell command with robust error handling
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print("[Speech] Speaking complete!")
    except subprocess.TimeoutExpired:
        logging.error("TTS timed out after 60 seconds.")
        print("[Speech] Error: TTS timed out.")
    except Exception as e:
        logging.error(f"Error in speak function: {e}")
        print(f"[Speech] Error: {e}")
    finally:
        # Brief pause for audio buffer to clear before resuming microphone
        time.sleep(0.5)
        is_speaking.clear()
        logging.info("is_speaking set to False") 


def speak(text):
    """Speak using Windows PowerShell (Microsoft David) - Non-blocking"""
    if not text:
        return
        
    text_without_emojis = remove_emojis(text)
    
    if not text_without_emojis.strip():
        print("[Speech] Nothing to speak after cleanup.")
        return
    
    # Run in a separate thread to avoid blocking the GUI
    t = threading.Thread(target=speak_thread_func, args=(text_without_emojis,))
    t.daemon = True
    t.start()


def init_tts():
    """Initialize TTS"""
    print("[Speech] Windows PowerShell TTS ready!")
    # Initialize pyttsx3 for voice info
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            print(f"[Speech] Voice set to: {voices[0].name}")
        engine.stop()
        print("[Speech] TTS engine initialized successfully!")
    except Exception as e:
        print(f"[Speech] pyttsx3 init info: {e}")


# Initialize
init_tts()

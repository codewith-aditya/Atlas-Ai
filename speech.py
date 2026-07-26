import pyttsx3
import logging
import threading
import re

# Initialize TTS engine and speaking state
engine = None
is_speaking = threading.Event()

def init_tts():
    """Initialize pyttsx3 engine only once."""
    global engine
    if engine is None:
        try:
            print("[Speech] Initializing pyttsx3 engine...")
            engine = pyttsx3.init()
            
            # Set voice properties
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)  # Use first available voice
                print(f"[Speech] Voice set to: {voices[0].name}")
            
            engine.setProperty('rate', 175)  # Optimized for faster but natural speech
            engine.setProperty('volume', 1.0)  # Maximum volume
            print("[Speech] TTS engine initialized successfully!")
        except Exception as e:
            print(f"[Speech] Error initializing TTS: {e}")

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
        "\U0001F650-\U0001F67F"  # Ornamental Dingbats
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def speak(text):
    """Speak the given text and toggle speaking state."""
    global engine
    
    text_without_emojis = remove_emojis(text)  # Remove emojis
    is_speaking.set()  # Speaking starts
    logging.info("is_speaking set to True")
    
    print(f"[Speech] Speaking: {text_without_emojis[:50]}...")
 
    try:
        # CRITICAL FIX: Reinitialize engine each time to avoid threading issues
        temp_engine = pyttsx3.init()
        temp_engine.setProperty('rate', 175)
        temp_engine.setProperty('volume', 1.0)
        
        temp_engine.say(text_without_emojis)
        temp_engine.runAndWait()
        temp_engine.stop()
        
        print("[Speech] Speaking complete!")
    except Exception as e:
        logging.error(f"Error in speak function: {e}")
        print(f"[Speech] Error: {e}")
    
    is_speaking.clear()  # Speaking ends
    logging.info("is_speaking set to False")

# Initialize TTS engine at the start
init_tts()

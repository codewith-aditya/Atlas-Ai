import logging
import threading
import re
import os
from elevenlabs import generate, play, set_api_key, voices

# Initialize speaking state
is_speaking = threading.Event()

# ElevenLabs API Key (set this in environment or here)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

def init_tts():
    """Initialize ElevenLabs TTS"""
    global ELEVENLABS_API_KEY
    if ELEVENLABS_API_KEY:
        set_api_key(ELEVENLABS_API_KEY)
        print("[Speech] ElevenLabs TTS initialized!")
    else:
        print("[Speech] WARNING: ElevenLabs API key not set!")
        print("[Speech] Set ELEVENLABS_API_KEY environment variable or add to speech.py")

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

def speak(text):
    """Speak using ElevenLabs TTS - High quality voice"""
    text_without_emojis = remove_emojis(text)
    is_speaking.set()
    logging.info("is_speaking set to True")
    
    print(f"[Speech] Speaking with ElevenLabs: {text_without_emojis[:50]}...")
 
    try:
        if not ELEVENLABS_API_KEY:
            print("[Speech] ERROR: ElevenLabs API key not set!")
            print("[Speech] Falling back to print...")
            print(f"[Would speak]: {text_without_emojis}")
            is_speaking.clear()
            return
        
        # Generate audio using ElevenLabs
        # Voice options: "Adam", "Antoni", "Arnold", "Bella", "Domi", "Elli", "Josh", "Rachel", "Sam"
        audio = generate(
            text=text_without_emojis,
            voice="Adam",  # Male voice, change to "Bella" for female
            model="eleven_monolingual_v1"
        )
        
        # Play the audio
        play(audio)
        
        print("[Speech] Speaking complete!")
    except Exception as e:
        logging.error(f"Error in speak function: {e}")
        print(f"[Speech] Error: {e}")
        print(f"[Speech] Fallback: {text_without_emojis}")
    
    is_speaking.clear()
    logging.info("is_speaking set to False")

# Initialize TTS at the start
init_tts()

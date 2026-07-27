import os
import time
import pyautogui
import google.generativeai as genai
from PIL import Image
import io

# Use the Gemini API Key we have
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class VisionModule:
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            # Use gemini-1.5-flash for fast vision capabilities
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.available = True
        else:
            self.available = False
            print("[Vision] Error: No API Key found.")

    def capture_screen(self):
        """Capture the current screen and return as PIL Image"""
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            return screenshot
        except Exception as e:
            print(f"[Vision] Screenshot error: {e}")
            return None

    def analyze_screen(self, query="What is on the screen?"):
        """
        Capture screen and ask Gemini about it.
        """
        if not self.available:
            return "Vision capabilities are not available (API Key missing)."

        print(f"[Vision] Analyzing screen with query: {query}")
        
        # Capture
        image = self.capture_screen()
        if not image:
            return "Failed to capture screen."

        try:
            # Generate content using Gemini Vision
            response = self.model.generate_content([query, image])
            return response.text.strip()
        except Exception as e:
            err_msg = str(e)
            print(f"[Vision] API Error: {err_msg}")
            if "404" in err_msg:
                return "Error: Vision model not found or API issue."
            return f"I encountered an error looking at the screen: {err_msg}"

# Global Instance
_vision_module = None

def analyze_user_screen(query):
    global _vision_module
    if _vision_module is None:
        _vision_module = VisionModule()
    
    return _vision_module.analyze_screen(query)

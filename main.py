import sys
import os
import time
import json
import threading
import psutil
import configparser  # For reading system.cfg
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

# ============================================================================
# AUTO-STARTUP SETUP - Runs on first launch
# ============================================================================
def setup_auto_startup():
    """Automatically add Atlas to Windows startup on first run"""
    try:
        # Check if already in startup
        startup_folder = os.path.join(
            os.environ['APPDATA'],
            r'Microsoft\Windows\Start Menu\Programs\Startup'
        )
        
        shortcut_path = os.path.join(startup_folder, "Atlas.bat")
        
        # If not in startup, add it
        if not os.path.exists(shortcut_path):
            atlas_dir = os.path.dirname(os.path.abspath(__file__))
            startup_script = os.path.join(atlas_dir, "START_ATLAS.bat")
            
            if os.path.exists(startup_script):
                import shutil
                shutil.copy2(startup_script, shortcut_path)
                print("✅ [AUTO-STARTUP] Atlas added to Windows startup!")
                print(f"📁 [AUTO-STARTUP] Location: {shortcut_path}")
            else:
                print("⚠️ [AUTO-STARTUP] START_ATLAS.bat not found, skipping auto-startup")
        else:
            print("ℹ️ [AUTO-STARTUP] Already in startup folder")
            
    except Exception as e:
        print(f"⚠️ [AUTO-STARTUP] Failed to add to startup: {e}")
        # Don't crash if startup setup fails

# Run auto-startup setup
setup_auto_startup()

# ============================================================================
# Continue with normal imports and setup
# ============================================================================


import pyautogui
import requests
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken
import webbrowser
import re
import urllib.parse
import pygame
import screen_brightness_control as sbc

# Groq API import
from groq import Groq

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QGridLayout, QPushButton,
    QHBoxLayout, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFontDatabase, QFont, QColor, QLinearGradient, QPalette, QBrush

# Local imports
from Gui import ASTRAUI
from automation import perform_automation_action, check_reminders
from speech_windows import speak, is_speaking  # Windows PowerShell TTS - 100% reliable
from listening import Listener
from listening_livekit import LiveKitListener  # LiveKit support
from Ai import process_with_ai_brain, get_ai_brain, get_proactive_suggestions  # AI Brain Module
from conversational_ai import get_conversational_ai, chat_naturally  # Reverted to Groq

def get_base_path():
    """Get the base path for the current execution."""
    if getattr(sys, 'frozen', False):  # If running as .exe
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    base_path = get_base_path()
    return os.path.join(base_path, relative_path)

# ------------------------------------------------------------------------------
# Point to the "materials" folder and essential files using resource_path
# ------------------------------------------------------------------------------
MATERIALS_PATH = resource_path('materials')
print(f"[DEBUG] MATERIALS_PATH resolved to: {MATERIALS_PATH}")  # Debugging Statement

# Verify that the materials folder exists
if not os.path.exists(MATERIALS_PATH):
    raise FileNotFoundError(f"Materials folder not found at: {MATERIALS_PATH}")

KEY_FILE = os.path.join(MATERIALS_PATH, 'system.cfg')
RECOVER_FILE = os.path.join(MATERIALS_PATH, 'recover.txt')
BACKGROUND_MUSIC_FILE = os.path.join(MATERIALS_PATH, 'brain_power_music.mp3')
PHONE_NUMBERS_FILE = os.path.join(MATERIALS_PATH, 'PhoneNumbers.txt')
WEATHER_API_KEY_FILE = os.path.join(MATERIALS_PATH, 'weather_api_key.txt')
INITIAL_PROMPT_FILE = os.path.join(MATERIALS_PATH, 'system.initialize')  # New File

# Debugging Statements for Essential Files
for file_path, description in [
    (KEY_FILE, "System Configuration File"),
    (RECOVER_FILE, "Recovery File"),
    (BACKGROUND_MUSIC_FILE, "Background Music File"),
    (PHONE_NUMBERS_FILE, "Phone Numbers File"),
    (WEATHER_API_KEY_FILE, "Weather API Key File"),
    (INITIAL_PROMPT_FILE, "Initial Prompt File")
]:
    if not os.path.exists(file_path):
        print(f"[ERROR] {description} not found at: {file_path}")
    else:
        print(f"[DEBUG] {description} found at: {file_path}")

PREDEFINED_SECURITY_KEY = '99ChEATlATdU510LwVpGllMROGguHSKyGk-z0GB3sRw='

CHAT_HISTORY_FILE = os.path.join(MATERIALS_PATH, "chat_history.json")
IMAGE_ANALYZER_HISTORY_FILE = os.path.join(MATERIALS_PATH, "image_analyzer_history.json")  # Added
REMINDERS = []
reminder_lock = threading.Lock()

# ============================================================================
# INTENT DETECTION - Detect if input is task or conversation
# ============================================================================
def is_task_command(user_input):
    """Detect if user input is a task command or natural conversation"""
    task_keywords = [
        'open', 'close', 'play', 'search', 'send', 'searching',
        'reminder', 'weather', 'time', 'news', 'playing',
        'brightness', 'volume', 'camera', 'cleaning', 'checking',
        'set', 'increase', 'decrease', 'turn', 'start', 'stop',
        'look', 'see', 'screen', 'vision', 'watch'  # [NEW] Vision keywords
    ]
    user_lower = user_input.lower()
    return any(keyword in user_lower for keyword in task_keywords)
# ============================================================================

KEY_DURATIONS = {
    "atlas-weekly-pro": timedelta(days=7),
    "atlas-monthly-elite": timedelta(days=30),
    "atlas-lifetime-master": None,  # no expiration
    "atlas-testing-key": timedelta(minutes=5),
}

try:
    fernet = Fernet(PREDEFINED_SECURITY_KEY.encode())
except ValueError as e:
    print(f"Invalid security key format: {e}")
    sys.exit(1)

# ------------------------------------------------------------------------------
# Function to Remove Emojis
# ------------------------------------------------------------------------------
def remove_emojis(text):
    """Remove emojis from the given text."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F1E0-\U0001F1FF"  # Flags
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# ------------------------------------------------------------------------------
# Subscription GUI Integrated into main.py
# ------------------------------------------------------------------------------
class SubscriptionGUI(QDialog):
    def __init__(self, materials_path, parent=None):
        super(SubscriptionGUI, self).__init__(parent)
        self.materials_path = materials_path
        self.setWindowTitle("ASTRA - Subscription Key")
        self.setFixedSize(500, 300)  # Increased size for better fit
        self.init_ui()

    def init_ui(self):
        # Set the entire background to black
        self.setStyleSheet("background-color: #000000;")  # Pure Black

        # Load and set fonts
        roboto_font_path = resource_path(os.path.join("materials", "Roboto-Regular.ttf"))

        if os.path.exists(roboto_font_path):
            QFontDatabase.addApplicationFont(roboto_font_path)  # Font for the labels
        else:
            print(f"Font file '{roboto_font_path}' not found.")

        # Fonts
        try:
            sci_fi_title_font = QFont("Audiowide", 22)
        except:
            sci_fi_title_font = QFont("Arial", 22)  # Fallback font

        professional_font = QFont("Roboto", 12)
        input_font = QFont("Orbitron", 12)

        # Layout
        layout = QGridLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title Label with Glowing Effect
        self.title_label = QLabel("ENTER SUBSCRIPTION KEY")
        self.title_label.setFont(sci_fi_title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #00FFFF;")  # Electric Cyan Blue
        self.apply_glow_effect(self.title_label, QColor(0, 255, 255, 160))  # Cyan Glow
        layout.addWidget(self.title_label, 0, 0, 1, 2)

        # Labels and Input Fields
        label_style = """
            QLabel {
                color: #39FF14; /* Neon Green */
                font-weight: bold;
                font-size: 14px;
            }
        """
        input_style = """
            QLineEdit {
                color: #00FFFF;                  /* Electric Cyan Blue text */
                background-color: #000000;       /* Black background */
                border: 2px solid #39FF14;       /* Neon Green border */
                padding: 10px;
                font-size: 14px;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #00FF7F;       /* Spring Green border on focus */
                background-color: #1A1A1A;       /* Darker black on focus */
            }
        """

        # Subscription Key
        self.key_label = QLabel("Subscription Key:")
        self.key_label.setFont(professional_font)
        self.key_label.setStyleSheet(label_style)
        layout.addWidget(self.key_label, 1, 0)

        # Input Field
        self.key_input = QLineEdit()
        self.key_input.setFont(input_font)
        self.key_input.setPlaceholderText("Enter your subscription key")
        self.key_input.setStyleSheet(input_style)
        layout.addWidget(self.key_input, 1, 1)

        # Save Button with Gradient and Hover Effect
        self.submit_button = QPushButton("Save")
        self.submit_button.setFont(QFont("Orbitron", 14))
        self.submit_button.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00FFFF, stop:1 #1E90FF
                );
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E90FF, stop:1 #00BFFF
                );
            }
        """)
        self.submit_button.clicked.connect(self.submit_key)

        # Add Save Button to Layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        button_layout.addStretch()
        layout.addLayout(button_layout, 2, 0, 1, 2)

        self.setLayout(layout)

        # Enable Enter Key Navigation
        self.enable_enter_key_navigation()

    def apply_glow_effect(self, widget, color):
        """Applies a glowing effect to a widget."""
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(color)
        glow.setOffset(0)
        widget.setGraphicsEffect(glow)

    def enable_enter_key_navigation(self):
        """Connect Enter key to move focus to the next input field or trigger save."""
        # Since there's only one input field, pressing Enter should trigger the Save button
        self.key_input.returnPressed.connect(self.submit_key)

    def submit_key(self):
        """Validate and accept the subscription key."""
        subscription_key = self.key_input.text().strip()

        if not subscription_key:
            QMessageBox.warning(self, "Input Error", "Subscription key cannot be empty.")
            return

        self.subscription_key = subscription_key
        self.accept()  # Close the dialog with Accepted status

    def get_subscription_key(self):
        """Retrieve the entered subscription key."""
        return self.subscription_key

# ------------------------------------------------------------------------------
# User Information GUI Integrated into main.py
# ------------------------------------------------------------------------------
class UserInfoGUI(QDialog):
    def __init__(self, materials_path, parent=None):
        super(UserInfoGUI, self).__init__(parent)
        self.materials_path = materials_path
        self.setWindowTitle("ASTRA - User Information")
        self.setFixedSize(600, 400)  # Increased size for better fit
        self.init_ui()

    def init_ui(self):
        # Set the entire background to black
        self.setStyleSheet("background-color: #000000;")  # Pure Black

        # Load and set fonts
        audiowide_font_path = resource_path(os.path.join("materials", "Audiowide-Regular.ttf"))
        roboto_font_path = resource_path(os.path.join("materials", "Roboto-Regular.ttf"))

        if os.path.exists(audiowide_font_path):
            QFontDatabase.addApplicationFont(audiowide_font_path)  # Font for the title
        else:
            print(f"Font file '{audiowide_font_path}' not found.")

        if os.path.exists(roboto_font_path):
            QFontDatabase.addApplicationFont(roboto_font_path)  # Font for the labels
        else:
            print(f"Font file '{roboto_font_path}' not found.")

        # Fonts
        try:
            sci_fi_title_font = QFont("Audiowide", 24)
        except:
            sci_fi_title_font = QFont("Arial", 24)  # Fallback font

        professional_font = QFont("Roboto", 12)
        input_font = QFont("Orbitron", 12)

        # Layout
        layout = QGridLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title Label with Glowing Effect
        self.title_label = QLabel("USER INFORMATION")
        self.title_label.setFont(sci_fi_title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #00FFFF;")  # Electric Cyan Blue
        self.apply_glow_effect(self.title_label, QColor(0, 255, 255, 160))  # Cyan Glow
        layout.addWidget(self.title_label, 0, 0, 1, 2)

        # Labels and Input Fields
        label_style = """
            QLabel {
                color: #00FFFF;                  /* Electric Cyan Blue */
                font-size: 14px;
                font-weight: bold;
            }
        """
        input_style = """
            QLineEdit {
                color: #FFFFFF;
                background-color: #000000;
                border: 2px solid #00FFFF;
                padding: 10px;
                font-size: 14px;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #1E90FF;
                background-color: #1A1A1A;
            }
        """

        # Name
        self.name_label = QLabel("Name:")
        self.name_label.setFont(professional_font)
        self.name_label.setStyleSheet(label_style)
        layout.addWidget(self.name_label, 1, 0)

        self.name_input = QLineEdit()
        self.name_input.setFont(input_font)
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setStyleSheet(input_style)
        layout.addWidget(self.name_input, 1, 1)

        # Age
        self.age_label = QLabel("Age:")
        self.age_label.setFont(professional_font)
        self.age_label.setStyleSheet(label_style)
        layout.addWidget(self.age_label, 2, 0)

        self.age_input = QLineEdit()
        self.age_input.setFont(input_font)
        self.age_input.setPlaceholderText("Enter your age")
        self.age_input.setStyleSheet(input_style)
        layout.addWidget(self.age_input, 2, 1)

        # City
        self.city_label = QLabel("City:")
        self.city_label.setFont(professional_font)
        self.city_label.setStyleSheet(label_style)
        layout.addWidget(self.city_label, 3, 0)

        self.city_input = QLineEdit()
        self.city_input.setFont(input_font)
        self.city_input.setPlaceholderText("Enter your city")
        self.city_input.setStyleSheet(input_style)
        layout.addWidget(self.city_input, 3, 1)

        # Interests
        self.interests_label = QLabel("Interests:")
        self.interests_label.setFont(professional_font)
        self.interests_label.setStyleSheet(label_style)
        layout.addWidget(self.interests_label, 4, 0)

        self.interests_input = QLineEdit()
        self.interests_input.setFont(input_font)
        self.interests_input.setPlaceholderText("Enter your interests (comma-separated)")
        self.interests_input.setStyleSheet(input_style)
        layout.addWidget(self.interests_input, 4, 1)

        # Save Button
        self.save_button = QPushButton("Save")
        self.save_button.setFont(QFont("Orbitron", 14))
        self.save_button.setFixedWidth(150)
        self.save_button.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00FFFF, stop:1 #1E90FF
                );
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1E90FF, stop:1 #00BFFF
                );
            }
        """)
        self.save_button.clicked.connect(self.save_user_info)

        # Add Save Button to Horizontal Layout for Centering
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        layout.addLayout(button_layout, 5, 0, 1, 2)

        self.setLayout(layout)

        # Enable Enter Key Navigation
        self.enable_enter_key_navigation()

    def apply_glow_effect(self, widget, color):
        """Applies a glowing effect to a widget."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(color)
        shadow.setOffset(0)
        widget.setGraphicsEffect(shadow)

    def enable_enter_key_navigation(self):
        """Connect Enter key to move focus to the next input field or trigger save."""
        # Connect Enter key in each input field to focus the next field
        self.name_input.returnPressed.connect(self.age_input.setFocus)
        self.age_input.returnPressed.connect(self.city_input.setFocus)
        self.city_input.returnPressed.connect(self.interests_input.setFocus)
        # In the last input field, pressing Enter will trigger the Save action
        self.interests_input.returnPressed.connect(self.save_user_info)

    def save_user_info(self):
        """Save user information and close the dialog."""
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        city = self.city_input.text().strip()
        interests = self.interests_input.text().strip()

        if not name or not age:
            QMessageBox.warning(self, "Input Error", "Name and Age are required fields.")
            return

        if not age.isdigit():
            QMessageBox.warning(self, "Input Error", "Age must be a number.")
            return

        self.user_data = {
            "name": name,
            "age": int(age), # Ensure age is stored as an integer
            "city": city if city else "Unknown",
            "interests": interests if interests else "General"
        }
        
        # NO speak here - will be handled by main flow
        print(f"✅ User info collected: {name}, {age}")
        self.accept()

    def get_user_data(self):
        """Retrieve the entered user data."""
        return self.user_data

# =========================================================================
#   Worker Thread for Handling the Conversation Loop
# =========================================================================
class ConversationWorker(QThread):
    userMessageSignal = pyqtSignal(str)
    botResponseSignal = pyqtSignal(str)
    finishedSignal    = pyqtSignal()

    def __init__(self, user_details=None, parent=None):
        super().__init__(parent)
        self._running = True
        self.user_details = user_details or {}
        self.chat_history = load_chat_history()
        # Removed appending system prompt to chat_history

        # Groq client initialization
        self.groq_client = None
        self.initialize_groq_client()

    def initialize_groq_client(self):
        """Initialize the Groq API client."""
        API_KEY = get_current_api_key()
        if not API_KEY:
            speak("API key is missing. Please provide a valid API key.")
            print("API key is missing.")
            sys.exit(1)
        self.groq_client = Groq(api_key=API_KEY)

    def process_user_input(self, command):
        """
        All the logic that used to be in the 'while True' loop for processing recognized user speech.
        This method can be called externally whenever new text is recognized.
        """
        print(f"[Worker] Received user command: {command}")
        self.userMessageSignal.emit(command)

        if "exit" in command or "quit" in command:
            speak("Goodbye! Have a great day.")
            self.stop()
            return

        # The rest of your existing logic for sending to Groq, etc.
        try:
            if not self.groq_client:
                self.initialize_groq_client()

            # Check if it's a task or conversation
            # Check if it's a task or conversation
            is_task = is_task_command(command)
            print(f"[DEBUG] Command: '{command}' | Is Task: {is_task}")
            
            if not is_task:
                # CONVERSATION MODE: Use conversational AI for natural chat
                print("[Worker] Conversation mode - using conversational AI")
                print(f"[DEBUG] Getting API key...")
                API_KEY = get_current_api_key()
                print(f"[DEBUG] API key obtained: {API_KEY[:10]}...")
                print(f"[DEBUG] Initializing conversational AI...")
                
                # Initialize with backend config from .env
                conv_ai = get_conversational_ai(groq_api_key=API_KEY)
                
                print(f"[DEBUG] Active backend: {conv_ai.backend} | Model: {conv_ai.active_model}")
                print(f"[DEBUG] Calling chat function...")
                enhanced_response = conv_ai.chat(command, user_name="Sir")
                print(f"[DEBUG] Response received: {enhanced_response[:50]}...")
                
                # Process through AI Brain for emotion/context/learning
                enhanced_response = process_with_ai_brain(command, enhanced_response)
                
                # Display and speak
                print(f"[DEBUG] Emitting to GUI...")
                self.botResponseSignal.emit(enhanced_response)
                print(f"[DEBUG] Speaking response...")
                speak(remove_emojis(enhanced_response))
                print(f"[DEBUG] Conversation mode complete!")
                
                # Save to history
                self.chat_history.append({"role": "user", "content": command})
                self.chat_history.append({"role": "assistant", "content": enhanced_response})
                save_chat_history(self.chat_history)
                return

            # TASK MODE: Continue with existing automation system
            print("[Worker] Task mode - using automation system")
            # Prepare messages using the new prepare_messages_for_groq function
            messages = prepare_messages_for_groq(
            command,
            CHAT_HISTORY_FILE,
            IMAGE_ANALYZER_HISTORY_FILE,
            user_details=self.user_details  # <-- IMPORTANT
            )

            # **Groq API request**
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Lighter model
                messages=messages,
                temperature=1,
                max_tokens=250,  # Reduced from 400
                top_p=1,
                stream=False,
                stop=None,
            )

            # Corrected attribute access using dot notation
            response_text = completion.choices[0].message.content.strip()

            if response_text:
                # Remove emojis from the response text for speaking
                filtered_response = remove_emojis(response_text)

                # Process through AI Brain for context/pattern learning
                response_text = process_with_ai_brain(
                    command, response_text, 
                    automation_action=response_text.split()[0] if response_text else None
                )

                # Append assistant response to chat_history
                if not response_text.startswith("#writing"):
                    self.botResponseSignal.emit(response_text)  # Emit text to GUI

                self.chat_history.append({"role": "assistant", "content": response_text})

                # Perform automation action (automation.py will handle speaking)
                perform_automation_action(response_text, self.user_details)

                # Save response to file
                save_response_to_file(response_text)
            else:
                print("No valid response from ASTRA.")

        except Exception as e:
            err_msg = f"Error in Conversation Loop: {e}"  # Generic error message
            print(err_msg)
            speak("Sorry, I encountered an error while processing your request.")

        # Append user message to chat_history
        self.chat_history.append({"role": "user", "content": command})
        save_chat_history(self.chat_history)

    def run(self):
        """
        If you still need a separate thread for any background tasks,
        you can keep them here. But the microphone listening no longer lives here.
        """
        while self._running:
            time.sleep(0.1)
        self.finishedSignal.emit()

    def stop(self):
        self._running = False
        print("[Worker] Stopping conversation worker...")

# =========================================================================
#   Helper Functions
# =========================================================================
def load_initial_prompt():
    """
    Load the initial prompt from the system.initialize file.
    Returns the content as a string.
    """
    INITIAL_PROMPT_FILE = os.path.join(MATERIALS_PATH, 'system.initialize')
    if not os.path.exists(INITIAL_PROMPT_FILE):
        error_message = f"Initial prompt file not found at: {INITIAL_PROMPT_FILE}"
        print(f"[ERROR] {error_message}")
        speak("Initial prompt file is missing. Please contact support.")
        sys.exit(1)
    try:
        with open(INITIAL_PROMPT_FILE, 'r', encoding='utf-8') as f:
            initial_prompt = f.read().strip()
            if not initial_prompt:
                raise ValueError("Initial prompt file is empty.")
            print("[DEBUG] Initial prompt loaded successfully.")
            return initial_prompt
    except Exception as e:
        error_message = f"Failed to load initial prompt: {e}"
        print(f"[ERROR] {error_message}")
        speak("Failed to load the initial prompt. Please contact support.")
        sys.exit(1)

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r") as f:
                history = json.load(f)
                if isinstance(history, list):
                    return history[-30:]  # Maintain up to last 30 messages
                else:
                    print(f"[ERROR] Expected a list in {CHAT_HISTORY_FILE}, got {type(history)}.")
                    return []
        except json.JSONDecodeError:
            speak("Chat history file is corrupted.")
            print(f"[ERROR] Chat history file {CHAT_HISTORY_FILE} is corrupted.")
            return []
    return []

def save_chat_history(history):
    recent_history = history[-30:]  # Keep last 30 messages
    try:
        with open(CHAT_HISTORY_FILE, "w") as f:
            json.dump(recent_history, f, indent=2)
        print(f"[DEBUG] Chat history saved with {len(recent_history)} messages.")
    except Exception as e:
        print(f"[ERROR] Failed to save chat history: {e}")

def save_response_to_file(response_text):
    clean_response = ''.join(c for c in response_text if c.isprintable())
    sci_fi_response = f"\x1b[96m{clean_response}\x1b[0m"
    print(sci_fi_response)

def get_time_based_greeting():
    hour = datetime.now().hour
    if 4 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Hello"

def is_subscription_valid(subscription_data, user_data):
    subscription_key = subscription_data.get("subscription_key")
    subscription_start = subscription_data.get("subscription_start")

    if not subscription_key or not subscription_start:
        return False, "No subscription details found."

    if subscription_key not in KEY_DURATIONS:
        return False, "Invalid subscription key."

    start_time = datetime.strptime(subscription_start, "%Y-%m-%d %H:%M:%S")
    if KEY_DURATIONS[subscription_key] is None:
        return True, "Initializing lifetime access."

    expire_time = start_time + KEY_DURATIONS[subscription_key]
    if datetime.now() > expire_time:
        return False, (
            "Your subscription has expired. Please renew your access.\n\n"
            "For assistance, contact:\nEmail: adityawakharkar99@gmail.com\n"
            "WhatsApp: 9309039729."
        )
    else:
        if subscription_key == "ASTRA-weekly-pro":
            activation_message = "Initializing weekly access."
        elif subscription_key == "ASTRA-monthly-elite":
            activation_message = "Initializing monthly access."
        elif subscription_key == "ASTRA-testing-key":
            activation_message = "5-minute test mode activated successfully."
        else:
            activation_message = "Subscription activated successfully."

        if not user_data.get("activation_notified", False):
            return True, activation_message, True
        return True, activation_message, False

def collect_subscription_key():
    print("Launching Subscription Key GUI...")
    speak("Enter your subscription key")

    subscription_dialog = SubscriptionGUI(materials_path=MATERIALS_PATH)
    result = subscription_dialog.exec_()

    if result == QDialog.Accepted:
        subscription_key = subscription_dialog.get_subscription_key()
        if subscription_key:
            return subscription_key
        else:
            print("No subscription key entered.")
            speak("No subscription key entered. Exiting.")
            sys.exit(1)
    else:
        print("Subscription key dialog was canceled.")
        speak("Subscription key entry was canceled. Exiting.")
        sys.exit(1)

def collect_user_details():
    print("Launching User Information GUI...")
    speak("Please enter your user information")

    user_info_dialog = UserInfoGUI(materials_path=MATERIALS_PATH)
    result = user_info_dialog.exec_()

    if result == QDialog.Accepted:
        user_data = user_info_dialog.get_user_data()
        if user_data:
            return user_data
        else:
            print("No user information entered.")
            speak("No user information entered. Exiting.")
            sys.exit(1)
    else:
        print("User information dialog was canceled.")
        speak("User information entry was canceled. Exiting.")
        sys.exit(1)

def encrypt_and_append_subscription_key(subscription_key):
    encrypted_key = fernet.encrypt(subscription_key.encode()).decode()
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'w') as f:
            f.write(PREDEFINED_SECURITY_KEY)

    with open(KEY_FILE, 'r') as f:
        content = f.read().strip()

    if content.count("/.") < 1:
        new_content = f"{content}/.{encrypted_key}"
        with open(KEY_FILE, 'w') as f:
            f.write(new_content)
        print("[DEBUG] Subscription key encrypted and appended to system.cfg.")

def save_user_data(user_data):
    user_data_json = json.dumps(user_data).encode()
    encrypted_user_data = fernet.encrypt(user_data_json).decode()

    with open(KEY_FILE, 'r') as f:
        content = f.read().strip()

    if content.count("/.") < 2:
        new_content = f"{content}/.{encrypted_user_data}"
        with open(KEY_FILE, 'w') as f:
            f.write(new_content)
        print("[DEBUG] User data encrypted and appended to system.cfg.")

def load_data_from_system_cfg():
    if not os.path.exists(KEY_FILE):
        # Auto-create the base key file for new users/developers
        print("[DEBUG] system.cfg not found. Creating a new one for first-time setup.")
        with open(KEY_FILE, 'w') as f:
            f.write(PREDEFINED_SECURITY_KEY)

    with open(KEY_FILE, 'r') as f:
        content = f.read().strip()

    if not content.startswith(PREDEFINED_SECURITY_KEY):
        error_message = "Error: system solution file not found. Please contact the Atlas team."
        print(error_message)
        speak(error_message)
        sys.exit(1)

    parts = content.split("/.")
    # parts[0] = PREDEFINED_SECURITY_KEY
    # parts[1] = encrypted_subscription_key (if present)
    # parts[2] = encrypted_user_data (if present)

    if len(parts) == 1:
        return False, False, None, None
    elif len(parts) == 2:
        encrypted_sub_key = parts[1]
        try:
            subscription_key = fernet.decrypt(encrypted_sub_key.encode()).decode()
        except InvalidToken:
            error_message = "Error: system solution file not found. Please contact the Atlas team."
            print(error_message)
            speak(error_message)
            sys.exit(1)
        return True, False, subscription_key, None
    elif len(parts) == 3:
        encrypted_sub_key = parts[1]
        encrypted_user_data = parts[2]
        try:
            subscription_key = fernet.decrypt(encrypted_sub_key.encode()).decode()
        except InvalidToken:
            error_message = "Error: system solution file not found. Please contact the Atlas team."
            print(error_message)
            speak(error_message)
            sys.exit(1)

        try:
            decrypted_user_data = fernet.decrypt(encrypted_user_data.encode()).decode()
            user_data = json.loads(decrypted_user_data)
            return True, True, subscription_key, user_data
        except InvalidToken:
            error_message = "Error: system solution file not found. Please contact the Atlas team."
            print(error_message)
            speak(error_message)
            sys.exit(1)
    else:
        error_message = "Error: system solution file not found. Please contact the Atlas team."
        print(error_message)
        speak(error_message)
        sys.exit(1)

def get_current_api_key():
    default_api_key = ""
    recover_file_path = os.path.join(MATERIALS_PATH, 'recover.txt')
    if os.path.exists(recover_file_path):
        try:
            with open(recover_file_path, 'r', encoding='utf-8') as f:
                user_api_key = f.read().strip()
            if user_api_key:
                return user_api_key
            else:
                return default_api_key
        except Exception as e:
            print(f"[ERROR] Error reading {recover_file_path}: {e}")
            return default_api_key
    else:
        return default_api_key

def play_background_music(music_file, volume=5
                          ):
    music_path = os.path.join(MATERIALS_PATH, music_file)
    # Attempt to play only if pygame is imported successfully
    try:
        pygame.mixer.init()
        if not os.path.exists(music_path):
            print(f"[WARNING] Music file '{music_file}' not found in materials folder. Skipping.")
            return
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        print("[DEBUG] Background music started.")
    except ImportError:
        print("[ERROR] pygame is not installed. Background music will be disabled.")
    except Exception as e:
        print(f"[ERROR] Failed to play background music: {e}")

# ------------------------------------------------------------------------------
# New Function: load_last_n_entries
# ------------------------------------------------------------------------------
def load_last_n_entries(file_path, n):
    """
    Load the last n entries from a JSON file. If the file does not exist, create it with an empty list.

    Args:
        file_path (str): Path to the JSON file.
        n (int): Number of entries to load.

    Returns:
        list: A list of the last n entries.
    """
    if not os.path.exists(file_path):
        print(f"[WARNING] {file_path} does not exist. Creating a new empty history file.")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"[ERROR] Expected a list in {file_path}, but got {type(data)}. Resetting to empty list.")
                data = []
                with open(file_path, 'w', encoding='utf-8') as fw:
                    json.dump(data, fw, indent=2)
                return []
            return data[-n:]
    except json.JSONDecodeError:
        print(f"[ERROR] Failed to decode JSON from {file_path}. Resetting to empty list.")
        with open(file_path, 'w', encoding='utf-8') as fw:
            json.dump([], fw, indent=2)
        return []
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while loading {file_path}: {e}")
        return []

# ------------------------------------------------------------------------------
# New Function: prepare_messages_for_groq
# ------------------------------------------------------------------------------
def prepare_messages_for_groq(command, chat_history_file, image_history_file, user_details=None):
    """
    Prepare the messages list for the Groq API by combining chat and image analyzer histories with the current command.

    Args:
        command (str): The current user query.
        chat_history_file (str): Path to chat_history.json.
        image_history_file (str): Path to image_analyzer_history.json.
        user_details (dict, optional): User details to include in the first API prompt.

    Returns:
        list: A list of message dictionaries.
    """
    messages = []

    # Load and append the initial prompt from system.initialize
    initial_prompt = load_initial_prompt()
    messages.append({"role": "system", "content": initial_prompt})

    # Append user details if available
    if user_details:
        user_details_str = json.dumps(user_details, indent=2)
        messages.append({"role": "system", "content": f"### User Details\n{user_details_str}"})

    # Add heading for Chat History
    messages.append({"role": "system", "content": "### Chat History (Last 6 Messages)"})

    # Load last 6 chat history messages
    chat_history = load_last_n_entries(chat_history_file, 6)
    if chat_history:
        for idx, msg in enumerate(chat_history, start=1):
            role = msg.get("role")
            content = msg.get("content")
            if role not in ["user", "assistant"]:
                print(f"[DEBUG] Invalid role in chat_history.json at index {idx}: {role}")
                continue  # Skip invalid entries
            if not content:
                print(f"[DEBUG] Missing content in chat_history.json at index {idx}.")
                continue  # Skip entries without content
            messages.append({"role": role, "content": content})
    else:
        print("[DEBUG] No chat history available to load.")

    # Add heading for Image Analysis History
    messages.append({"role": "system", "content": "### Image Analysis History (Last 2 Messages)"})

    # Load last 2 image analyzer history messages
    image_history_entries = load_last_n_entries(image_history_file, 2)
    if image_history_entries:
        for idx, entry in enumerate(image_history_entries, start=1):
            response = entry.get("after seeing the image")
            if response:
                messages.append({"role": "assistant", "content": response})
            else:
                print(f"[DEBUG] Image analyzer history entry missing 'response' at index {idx}: {entry}")
    else:
        print("[DEBUG] No image analyzer history available to load.")

    # Add heading for Current Query
    messages.append({"role": "system", "content": "### Current Query"})

    # Append current user query
    if command:
        messages.append({"role": "user", "content": command})
    else:
        print("[DEBUG] No user command provided.")

    # Debug: Print the prepared messages
    print("[DEBUG] Prepared messages for Groq API:")
    for i, msg in enumerate(messages):
        role = msg.get("role")
        content_preview = msg.get("content")[:50] + ("..." if len(msg.get("content", "")) > 50 else "")
        print(f"  Message {i}: Role={role}, Content={content_preview}")

    # Optional: Validate the messages list
    valid_roles = {"system", "user", "assistant"}
    for i, msg in enumerate(messages):
        role = msg.get("role")
        content = msg.get("content")
        if role not in valid_roles:
            print(f"[ERROR] Invalid role '{role}' in message {i}.")
        if not isinstance(content, str) or not content.strip():
            print(f"[ERROR] Invalid or empty content in message {i}.")

    return messages

# =========================================================================
#   MAIN FUNCTION
# =========================================================================
# =========================================================================
def main():
    # Initialize QApplication first
    app = QApplication(sys.argv)
    app.setFont(QFont("Orbitron", 14))

    try:
        has_valid_cfg, has_user_data, subscription_key, user_data = load_data_from_system_cfg()
    except SystemExit:
        return

    # Start reminders in the background
    reminder_thread = threading.Thread(target=check_reminders, daemon=True)
    reminder_thread.start()

    # If no subscription key & no user data, collect subscription key
    if not has_valid_cfg and not has_user_data:
        entered_key = collect_subscription_key()
        if not entered_key:
            speak("Subscription key entry was canceled. Exiting.")
            print("Subscription key dialog was canceled.")
            sys.exit(0)
        
        encrypt_and_append_subscription_key(entered_key)
        speak("Subscription key saved successfully!")
        print("✅ Subscription key saved!")
        # Re-load data to continue
        has_valid_cfg, has_user_data, subscription_key, user_data = load_data_from_system_cfg()

    # If subscription key exists but no user data, collect user details
    if has_valid_cfg and not has_user_data:
        user_details = collect_user_details()
        if not user_details:
            speak("User information entry was canceled. Exiting.")
            print("User information dialog was canceled.")
            sys.exit(0)
        
        subscription_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration = None
        unit = None
        
        if subscription_key == "atlas-weekly-pro":
            duration = 7
            unit = "days"
        elif subscription_key == "atlas-monthly-elite":
            duration = 30
            unit = "days"
        elif subscription_key == "atlas-lifetime-master":
            duration = None
            unit = None
        elif subscription_key == "atlas-testing-key":
            duration = 10
            unit = "minutes"

        new_data = {
            "subscription_data": {
                "subscription_key": subscription_key,
                "subscription_start": subscription_start,
                "duration": duration,
                "unit": unit
            },
            "user_details": user_details,
            "activation_notified": False
        }
        save_user_data(new_data)
        print("✅ User details saved!")
        # Re-load data to continue
        has_valid_cfg, has_user_data, subscription_key, user_data = load_data_from_system_cfg()


    # Validate subscription
    subscription_data = user_data.get("subscription_data")
    user_details = user_data.get("user_details")

    valid_response = is_subscription_valid(subscription_data, user_data)
    valid = valid_response[0]
    message = valid_response[1]
    rest = valid_response[2:] if len(valid_response) > 2 else []

    if not valid:
        speak(message)
        print(message)
        time.sleep(5)
        sys.exit(0)
    else:
        if len(rest) > 0 and rest[0]:
            print(message)

    # Greeting
    greeting = get_time_based_greeting()
    user_name = user_details.get("name", "User")
    welcome_message = f"{greeting}, {user_name}! How can I assist you today?"

    # Background music
    play_background_music("brain_power_music.mp3", volume=0.05)

    # Launch PyQt GUI
    try:
        ui = ASTRAUI()  # from Gui.py
    except Exception as e:
        print(f"[ERROR] Failed to initialize AtlasUI: {e}")
        speak("Failed to initialize the main interface. Please contact support.")
        sys.exit(1)

    ui.show()

# AUTO-START (from auto_start.py)



    # Speak the welcome message with debug print
    def delayed_speak():
        print(f"[DEBUG] Speaking welcome message: {welcome_message}")
        speak(welcome_message)
        print("[DEBUG] Finished speaking welcome message.")

    QTimer.singleShot(100, delayed_speak)

    # Set up conversation thread
    conv_worker = ConversationWorker(user_details=user_details)
    conv_worker.userMessageSignal.connect(ui.update_user_said_in_gui)
    conv_worker.botResponseSignal.connect(ui.append_bot_response_in_gui)
    conv_worker.start()

    # Create listener - Try LiveKit first, fallback to Google Speech
    listener = None
    use_livekit = False  # Disabled - LiveKit async connection issues, using Google Speech
    
    if use_livekit:
        try:
            print("[Main] Attempting to use LiveKit for voice recognition...")
            listener = LiveKitListener(
                on_recognized_callback=lambda cmd: conv_worker.process_user_input(cmd),
                on_error_callback=lambda err: print(f"[Main] LiveKit Error: {err}")
            )
            listener.daemon = True
            listener.start()
            print("[Main] LiveKit listener started successfully!")
        except Exception as e:
            print(f"[Main] LiveKit failed: {e}. Falling back to Google Speech Recognition...")
            listener = None
    
    # Fallback to Google Speech Recognition
    if listener is None:
        print("[Main] Using Google Speech Recognition...")
        listener = Listener(
            on_recognized_callback=lambda cmd: conv_worker.process_user_input(cmd),
            on_error_callback=lambda err: print(f"[Main] Listening Error: {err}"),
            phrase_time_limit=30, 
            pause_threshold=0.7
        )
        listener.daemon = True
        listener.start()

    # Link the listener to the GUI for mic toggle functionality
    ui.set_listener(listener)  # <-- Add this line to link Listener to GUI

    # Clean up on close
    def on_app_close():
        print("[Main] Application is closing. Cleaning up...")
        listener.stop()
        listener.join()    # Since it's a threading.Thread
        conv_worker.stop()
        conv_worker.wait(3000) # Since it's a QThread
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            print("[Main] Pygame mixer stopped.")
        except Exception as e:
            print(f"[ERROR] Error stopping pygame mixer: {e}")
        print("[Main] Cleanup complete.")

    app.aboutToQuit.connect(on_app_close)
    sys.exit(app.exec_())

# =========================================================================
#   ENTRY POINT
# =========================================================================
if __name__ == "__main__":
    main()
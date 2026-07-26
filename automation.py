# automation.py

import sys
import os
import time
import json
import subprocess
import threading
import queue
import psutil
import pyautogui
import requests
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken
import google.generativeai as genai
import webbrowser
import re
import urllib.parse
import screen_brightness_control as sbc
import image_analyzer
from pygame import mixer
import logging
import camera_module
from speech_windows import speak, is_speaking  # Windows PowerShell TTS
import pygetwindow as gw
import win32gui
import win32con
from google_search import GoogleSearch  # Google Search integration
from gemini_ai import GeminiAI  # Gemini AI integration
from vision_module import analyze_user_screen  # Vision capabilities

# -------------------- Logging Setup --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# ------------------------------------------------------------------------------
# Determine BASE_DIR from execution context
# ------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    # Running inside a compiled executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running in normal Python mode
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MATERIALS_PATH = os.path.join(BASE_DIR, 'materials')
BACKGROUND_MUSIC_FILE = os.path.join(MATERIALS_PATH, 'brain_power_music.mp3')
WEATHER_API_KEY_FILE = os.path.join(MATERIALS_PATH, 'weather_api_key.txt')  # For OpenWeatherMap key
PHONE_NUMBERS_FILE = os.path.join(MATERIALS_PATH, 'PhoneNumbers.txt')      # For WhatsApp contacts

REMINDERS = []
reminder_lock = threading.Lock()

def close_window_by_name(target_name):
    """
    Close any window whose title contains the given target_name.
    """
    def enum_handler(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if window_title and target_name.lower() in window_title.lower():
                print(f"Found matching window: '{window_title}' (hwnd={hwnd})")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                

    win32gui.EnumWindows(enum_handler, None)


# -------------------- Helper Function: Send WhatsApp Message --------------------
def send_whatsapp_message(contact_name, message):
    """
    Sends a WhatsApp message to the specified contact.
    """
    try:
        if not os.path.exists(PHONE_NUMBERS_FILE):
            speak("Phone numbers file is missing.")
            logging.error("PhoneNumbers.txt file is missing.")
            return

        with open(PHONE_NUMBERS_FILE, 'r') as f:
            lines = f.readlines()

        contact_found = False
        phone_number = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            if ':' not in line:
                logging.warning(f"Incorrectly formatted line: {line}")
                continue
            name, number = line.split(':', 1)
            name = name.strip().lower()
            number = number.strip()
            if name == contact_name.lower():
                contact_found = True
                phone_number = number
                break

        if not contact_found:
            speak(f"The contact {contact_name} does not exist in the phone numbers file.")
            logging.warning(f"Contact '{contact_name}' not found.")
            return

        # Validate phone number format (e.g., +1234567890)
        if not re.match(r'^\+\d{10,15}$', phone_number):
            speak(f"The phone number for {contact_name} is incorrectly formatted.")
            logging.warning(f"Incorrectly formatted phone number for {contact_name}: {phone_number}")
            return

        # URL encode the message
        encoded_message = urllib.parse.quote(message)

        # Create WhatsApp URL
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"

        # Open the URL in the default browser
        webbrowser.open(whatsapp_url)
        speak(f"Sending your message to {contact_name} on WhatsApp.")
        logging.info(f"Opened WhatsApp URL for {contact_name} with message: {message}")

        # Optionally, automate pressing 'Enter' to send the message
        time.sleep(20)  # Adjust based on internet speed
        pyautogui.press('enter')

    except Exception as e:
        logging.error(f"Error sending WhatsApp message: {e}")
        speak("An error occurred while trying to send the WhatsApp message.")

# -------------------- Helper Function: Play Song on YouTube --------------------
def play_song_on_youtube(song_name):
    """
    Searches YouTube for the given song name and plays the most relevant video.
    """
    search_query = '+'.join(song_name.split())
    search_url = f"https://www.youtube.com/results?search_query={search_query}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/87.0.4280.141 Safari/537.36"
        )
    }
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            speak("Sorry, I couldn't reach YouTube.")
            logging.error(f"Failed to reach YouTube. Status code: {response.status_code}")
            return False

        html = response.text
        # Use regex to find video IDs in the search results
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        if video_ids:
            video_id = video_ids[0]
            video_url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
            speak(f"Playing {song_name} on YouTube, sir.")  # Speak FIRST
            webbrowser.open(video_url)
            logging.info(f"Playing song '{song_name}' on YouTube with video ID: {video_id}")

            # Optionally, automate pressing 'k' to play/pause the video
            time.sleep(7)  # Adjust delay based on internet speed
            pyautogui.press('k')  # Toggle play/pause on YouTube
            return True
        else:
            speak("Sorry, I couldn't find the song on YouTube.")
            logging.warning(f"No video IDs found for song '{song_name}' on YouTube.")
            return False
    except Exception as e:
        logging.error(f"Error in play_song_on_youtube: {e}")
        speak("An error occurred while trying to play the song.")
        return False

# -------------------- Helper Function: Close Unwanted Processes --------------------
def close_unwanted_processes(wait_seconds=3):
    """
    Closes common browser processes (Chrome, Edge, Firefox, Opera, Brave),
    Notepad & Calculator, then waits a few seconds.
    """
    logging.info("Closing unwanted processes...")
    print("\n[Cleaning Initialization] Closing browsers, notepad, and calculator...\n")

    processes_to_close = {
        "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe",
        "notepad.exe", "calc.exe"
    }

    for proc in psutil.process_iter(['pid', 'name']):
        name = (proc.info['name'] or "").lower().strip()
        if name in processes_to_close:
            try:
                proc.terminate()
                proc.wait(timeout=3)
                logging.info(f"Terminated process: {name} (PID: {proc.pid})")
            except psutil.NoSuchProcess:
                logging.warning(f"Process {name} (PID: {proc.pid}) already closed.")
            except psutil.AccessDenied:
                logging.error(f"Access denied terminating {name} (PID: {proc.pid}).")
            except psutil.TimeoutExpired:
                logging.error(f"Timeout: {name} (PID: {proc.pid}) did not close in time.")
            except Exception as e:
                logging.error(f"Failed to terminate {name} (PID: {proc.pid}). Error: {e}")

    time.sleep(wait_seconds)
    logging.info(f"Closed unwanted processes and waited for {wait_seconds} seconds.")
    print(f"[Cleaning Initialization] Done. Waited {wait_seconds}s.\n")

# -------------------- Helper Function: Get Weather API Key --------------------
def get_weather_api_key():
    """
    Retrieves the OpenWeatherMap API key from weather_api_key.txt.
    """
    if not os.path.exists(WEATHER_API_KEY_FILE):
        speak("Weather API key file is missing.")
        logging.error("weather_api_key.txt file is missing.")
        return None

    try:
        with open(WEATHER_API_KEY_FILE, 'r') as f:
            api_key = f.read().strip()
            if not api_key:
                speak("Weather API key is empty.")
                logging.warning("Weather API key is empty.")
                return None
            return api_key
    except Exception as e:
        speak("Failed to read weather API key.")
        logging.error(f"Error reading weather API key file: {e}")
        return None

# -------------------- Helper Function: Get Weather Info --------------------
def get_weather_info(city):
    """
    Fetches weather information for the specified city using OpenWeatherMap API
    and speaks the current weather conditions.
    """
    if not city:
        speak("No city specified for weather checking.")
        logging.warning("No city specified for weather checking.")
        return

    api_key = get_weather_api_key()
    if not api_key:
        return

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }

    try:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            speak(f"Sorry, I couldn't retrieve the weather information for {city}.")
            logging.error(f"Failed to fetch weather data for {city}. Status code: {response.status_code}")
            return

        data = response.json()
        if data.get("cod") != 200:
            message = data.get("message", "")
            speak(f"Sorry, I couldn't find weather information for {city}. {message}")
            logging.error(f"Weather API error for {city}: {message}")
            return

        weather_desc = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        weather_info = (
            f"The current weather in {city} is {weather_desc} with a temperature of "
            f"{temperature} degrees Celsius, humidity at {humidity}%, "
            f"and wind speed of {wind_speed} meters per second."
        )

        logging.info(f"Weather info for {city}: {weather_info}")
        print(weather_info)
        speak(weather_info)

    except Exception as e:
        speak("An error occurred while fetching the weather information.")
        logging.error(f"Exception in get_weather_info for {city}: {e}")

# -------------------- Helper Function: Validate and Set Reminder --------------------
def validate_and_set_reminder(reminder_time_str):
    """
    Validates and sets a reminder time. Accepts multiple time formats
    and normalizes to a full datetime object for the next occurrence.
    """
    reminder_time_str = reminder_time_str.lower().replace(".", "").replace("!", "").replace("?", "").strip()

    # Insert a space before 'am'/'pm' if missing
    if reminder_time_str.endswith('am') or reminder_time_str.endswith('pm'):
        if not reminder_time_str.endswith(' am') and not reminder_time_str.endswith(' pm'):
            reminder_time_str = reminder_time_str[:-2] + ' ' + reminder_time_str[-2:]

    # Possible time formats to try
    time_formats = ["%I:%M %p", "%I:%M%p", "%H:%M"]

    parsed_time = None
    for fmt in time_formats:
        try:
            parsed_time = datetime.strptime(reminder_time_str, fmt)
            break
        except ValueError:
            continue

    if parsed_time:
        now = datetime.now()
        reminder_datetime = now.replace(
            hour=parsed_time.hour,
            minute=parsed_time.minute,
            second=0,
            microsecond=0
        )
        # If the time has already passed today, set for tomorrow
        if reminder_datetime <= now:
            reminder_datetime += timedelta(days=1)

        with reminder_lock:
            REMINDERS.append({"time": reminder_datetime, "triggered": False})
        logging.info(f"Reminder scheduled for {reminder_datetime.strftime('%Y-%m-%d %I:%M %p')}.")
        speak(f"Sir, your reminder has been scheduled for {reminder_datetime.strftime('%I:%M %p')}.")
        return True
    else:
        logging.warning(f"Invalid time format for reminder: '{reminder_time_str}'.")
        speak("Sorry, I cannot set a reminder for that time.")
        return False

# -------------------- Helper Function: Check Reminders --------------------
def check_reminders():
    """
    Background loop that checks if it's time for any reminder every 30 seconds.
    """
    while True:
        now = datetime.now()
        with reminder_lock:
            for reminder in REMINDERS:
                if not reminder["triggered"] and now >= reminder["time"]:
                    reminder_time_formatted = reminder['time'].strftime('%I:%M %p')
                    speak(f"Sir, this is your scheduled reminder for {reminder_time_formatted}.")
                    logging.info(f"Reminder triggered for {reminder_time_formatted}.")
                    reminder["triggered"] = True
            # Remove triggered reminders
            REMINDERS[:] = [r for r in REMINDERS if not r["triggered"]]
        time.sleep(30)  # Check every 30 seconds

# -------------------- Helper Function: Perform Automation Action --------------------
def perform_automation_action(response, user_details):
    """
    Check for single-line automation instructions from the LLM
    and execute them. E.g., "open youtube", "cleaning initializing", etc.
    """
    raw_response = response.strip()
    logging.info(f"Raw API response: '{raw_response}'")  # Log raw response

    action = raw_response.lower().rstrip('.!?')
    logging.info(f"Processed action: '{action}'")  # Log processed action

    action = response.strip().lower().rstrip('.!?')
    user_city = user_details.get("city", "") if user_details else ""

    logging.info(f"Performing automation action: '{action}'")

    if action == "cleaning initializing":
        close_unwanted_processes(wait_seconds=3)
        return
    if action.startswith("close tab "):
        tab_name = action[len("close tab "):].strip()
        if not tab_name:
            logging.warning("Tab name not specified for 'close tab' command.")
            speak("Please specify the tab name to close.")
        else:
            try:
                close_window_by_name(tab_name)
                logging.info(f"Attempted to close tab: {tab_name}.")
            except Exception as e:
                logging.error(f"Error closing tab '{tab_name}': {e}")
                speak(f"An error occurred while closing the tab '{tab_name}'.")
        return

        
    if action.startswith("close app") or action.startswith("closing app") or (action.startswith("close ") and "tab" not in action and "youtube" not in action and "camera" not in action):
        app_name = action.replace("close app", "").replace("closing app", "").replace("close ", "").replace("closing ", "").strip()
        if not app_name:
            logging.warning("App name not specified for 'close app' command.")
            speak("Please specify the app name to close.")
            return
        try:
            print(f"close {app_name}")  # Debug output
            closed = False
            for process in psutil.process_iter(['name']):
                if process.info['name'] and app_name.lower() in process.info['name'].lower():
                    process.terminate()
                    logging.info(f"Closed application: {process.info['name']} (PID: {process.pid})")
                    speak(f"Closed {app_name}, sir.")
                    closed = True
                    break
            if not closed:
                logging.warning(f"Application '{app_name}' not found.")
                speak(f"Application '{app_name}' is not running.")
        except Exception as e:
            logging.error(f"An error occurred while closing the application '{app_name}': {e}")
            speak(f"An error occurred while closing {app_name}.")
        return

    if "background music turning off" in action:
        try:
            mixer.music.stop()
            logging.info("Background music turned off.")
            speak("Background music has been turned off, sir.")
        except Exception as e:
            logging.error(f"Error turning off background music: {e}")
            speak("An error occurred while turning off the background music.")
        return

    if "background music turning on" in action:
        try:
            mixer.music.load(BACKGROUND_MUSIC_FILE)
            mixer.music.play(-1)  # Play on loop
            logging.info("Background music turned on.")
            speak("Background music has been turned on, sir.")
        except Exception as e:
            logging.error(f"Error turning on background music: {e}")
            speak("An error occurred while turning on the background music.")
        return

    if "increase the brightness" in action and "%" not in action:
        try:
            current_brightness = sbc.get_brightness()[0]
            new_brightness = min(current_brightness + 10, 100)
            sbc.set_brightness(new_brightness)
            speak(f"Brightness increased to {new_brightness} percent, sir.")
        except Exception as e:
            logging.error(f"Error increasing brightness: {e}")
        return

    if "decrease the brightness" in action and "%" not in action:
        try:
            current_brightness = sbc.get_brightness()[0]
            new_brightness = max(current_brightness - 10, 0)
            sbc.set_brightness(new_brightness)
            speak(f"Brightness decreased to {new_brightness} percent, sir.")
        except Exception as e:
            logging.error(f"Error decreasing brightness: {e}")
        return

    if "increase the brightness " in action and "%" in action:
        try:
            percentage = int(action.split(" ")[-1].replace("%", ""))
            current_brightness = sbc.get_brightness()[0]
            new_brightness = min(current_brightness + percentage, 100)
            sbc.set_brightness(new_brightness)
            speak(f"Brightness increased by {percentage} percent to {new_brightness} percent, sir.")
        except Exception as e:
            logging.error(f"Error increasing brightness by percentage: {e}")
        return

    if "decrease the brightness " in action and "%" in action:
        try:
            percentage = int(action.split(" ")[-1].replace("%", ""))
            current_brightness = sbc.get_brightness()[0]
            new_brightness = max(current_brightness - percentage, 0)
            sbc.set_brightness(new_brightness)
            speak(f"Brightness decreased by {percentage} percent to {new_brightness} percent, sir.")
        except Exception as e:
            logging.error(f"Error decreasing brightness by percentage: {e}")
        return

    if "increase the volume" in action and "%" not in action:
        try:
            for _ in range(4):
                pyautogui.press("volumeup")
            speak("Volume increased by 10 percent, sir.")
        except Exception as e:
            logging.error(f"Error increasing volume: {e}")
        return

    if "decrease the volume" in action and "%" not in action:
        try:
            for _ in range(4):
                pyautogui.press("volumedown")
            speak("Volume decreased by 10 percent, sir.")
        except Exception as e:
            logging.error(f"Error decreasing volume: {e}")
        return

    if "increase the volume " in action and "%" in action:
        try:
            percentage = int(action.split(" ")[-1].replace("%", ""))
            steps = int(percentage / 2.5)
            for _ in range(steps):
                pyautogui.press("volumeup")
            speak(f"Volume increased by {percentage} percent, sir.")
        except Exception as e:
            logging.error(f"Error increasing volume by percentage: {e}")
        return

    if "decrease the volume " in action and "%" in action:
        try:
            percentage = int(action.split(" ")[-1].replace("%", ""))
            steps = int(percentage / 2.5)
            for _ in range(steps):
                pyautogui.press("volumedown")
            speak(f"Volume decreased by {percentage} percent, sir.")
        except Exception as e:
            logging.error(f"Error decreasing volume by percentage: {e}")
        return

    if "reminder set for" in action:
        phrase = "reminder set for"
        start_idx = action.find(phrase)
        if start_idx != -1:
            reminder_time_str = action[start_idx+len(phrase):].strip(" .!?")
            if validate_and_set_reminder(reminder_time_str):
                logging.info(f"Reminder scheduled for {reminder_time_str}.")
            else:
                logging.warning("Invalid time for reminder.")
        return

    if action.startswith("#writing"):
       content = action[len("#writing "):].strip()
       if content:
           try:
               import writing_module
               writing_module.write_to_notepad(content)
               logging.info("Content written to Notepad successfully.")
           except Exception as e:
               logging.error(f"Error in writing content to Notepad: {e}")
       return   

    if "opening camera" in action:
        result = camera_module.open_camera()
        logging.info(result)
        return

    if "visual scanning" in action:
        result = camera_module.capture_image(folder_path="analyzer")
        logging.info(result)
        return

    if "closing camera" in action:
        result = camera_module.close_camera()
        logging.info(result)
        return

    if "open youtube" in action or "opening youtube" in action:
        try:
            speak("Opening YouTube, sir.")
            subprocess.Popen(["cmd", "/c", "start", "chrome", "https://www.youtube.com"], shell=True)
            logging.info("Opened YouTube.")
        except Exception as e:
            logging.error(f"Error opening YouTube: {e}")
            speak("An error occurred while opening YouTube.")
        return

    if "close youtube" in action or "closing youtube" in action:
        def close_youtube_tab():
            windows = gw.getAllTitles()
            for window in windows:
                if "YouTube" in window:
                    target_window = gw.getWindowsWithTitle(window)[0]
                    target_window.activate()
                    time.sleep(1)
                    pyautogui.hotkey('ctrl', 'w')
                    logging.info(f"Closed YouTube tab: {window}.")
                    speak("Closed YouTube, sir.")
                    return
            logging.warning("YouTube window not found.")
            speak("YouTube is not open, sir.")
        try:
            close_youtube_tab()
        except Exception as e:
            logging.error(f"Error closing YouTube tab: {e}")
            speak("An error occurred while closing YouTube.")
        return
    

    if "checking time" in action:
        current_time = datetime.now().strftime("%I:%M %p")
        speak(f"Sir, the current time is {current_time}.")
        logging.info(f"Time checked: {current_time}")
        return

    if "open google" in action or "opening google" in action:
        try:
            speak("Opening Google, sir.")
            subprocess.Popen(["cmd", "/c", "start", "chrome", "https://www.google.com"], shell=True)
            logging.info("Opened Google.")
        except Exception as e:
            logging.error(f"Error opening Google: {e}")
            speak("An error occurred while opening Google.")
        return

    if "open notepad" in action or "opening notepad" in action:
        try:
            speak("Opening Notepad, sir.")
            subprocess.Popen(["cmd", "/c", "start", "notepad"], shell=True)
            logging.info("Opened Notepad.")
        except Exception as e:
            logging.error(f"Error opening Notepad: {e}")
            speak("An error occurred while opening Notepad.")
        return

    if "open calculator" in action or "opening calculator" in action:
        try:
            speak("Opening Calculator, sir.")
            subprocess.Popen(["cmd", "/c", "start", "calc"], shell=True)
            logging.info("Opened Calculator.")
        except Exception as e:
            logging.error(f"Error opening Calculator: {e}")
            speak("An error occurred while opening Calculator.")
        return

    if action.startswith("open app ") or action.startswith("opening app ") or (action.startswith("open ") and "youtube" not in action and "google" not in action and "notepad" not in action and "calculator" not in action and "camera" not in action and "website" not in action):
        app_name = action.replace("open app", "").replace("opening app", "").replace("open ", "").replace("opening ", "").strip()
        if not app_name:
            logging.warning("App name not specified for 'open app' command.")
            speak("Please specify the app name to open.")
            return
        try:
            print(f"open {app_name}")
            speak(f"Opening {app_name}, sir.")
            pyautogui.hotkey('win', 's')
            time.sleep(1)
            pyautogui.typewrite(app_name, interval=0.1)
            time.sleep(1)
            pyautogui.press('enter')
            logging.info(f"Opened application: {app_name}.")
        except Exception as e:
            logging.error(f"Error opening application '{app_name}': {e}")
            speak(f"An error occurred while opening {app_name}.")
        return

    if action.startswith("open website ") or action.startswith("opening website "):
        website_name = action.replace("open website", "").replace("opening website", "").strip()
        if website_name:
            url = f"https://{website_name}"
            try:
                speak(f"Opening {website_name}, sir.")
                subprocess.Popen(["cmd", "/c", "start", "chrome", url], shell=True)
                logging.info(f"Opened website: {url}.")
            except Exception as e:
                logging.error(f"Error opening website '{website_name}': {e}")
                speak(f"An error occurred while opening {website_name}.")
        else:
            logging.warning("Website name not specified for 'open website' command.")
            speak("Please specify a website name to open.")
        return

    if "checking weather" in action:
        get_weather_info(user_city)
        return

    if "opening latest news" in action:
        news_url = "https://www.youtube.com/results?search_query=latest+news"
        try:
            speak("Opening latest news, sir.")
            subprocess.Popen(["cmd", "/c", "start", "chrome", news_url], shell=True)
            logging.info("Opened latest news on YouTube.")
        except Exception as e:
            logging.error(f"Error opening latest news: {e}")
            speak("An error occurred while opening the latest news.")
        return

    if "searching on google" in action or "search google" in action:
        search_term = action.replace("searching on google", "").replace("search google", "").replace("for", "").strip()
        if search_term:
            encoded_search = '+'.join(search_term.split())
            url = f"https://www.google.com/search?q={encoded_search}"
            try:
                speak(f"Searching for {search_term} on Google, sir.")
                webbrowser.open(url)
                logging.info(f"Searched for '{search_term}' on Google.")
            except Exception as e:
                logging.error(f"Error searching for '{search_term}' on Google: {e}")
                speak(f"An error occurred while searching for {search_term} on Google.")
        else:
            logging.warning("Search term not specified for 'searching on google' command.")
            speak("Please provide a search term for Google.")
        return

    elif action.startswith("searching on youtube "):
        search_term = action[len("searching on youtube "):].strip()
        if search_term:
            encoded_search = '+'.join(search_term.split())
            url = f"https://www.youtube.com/results?search_query={encoded_search}"
            try:
                speak(f"Searching for {search_term} on YouTube, sir.")  # Speak FIRST
                webbrowser.open(url)
                logging.info(f"Searched for '{search_term}' on YouTube.")
            except Exception as e:
                logging.error(f"Error searching for '{search_term}' on YouTube: {e}")
                speak(f"An error occurred while searching for {search_term} on YouTube.")
        else:
            logging.warning("Search term not specified for 'searching on youtube' command.")
            speak("Please provide a search term for YouTube.")
        return

    elif action.startswith("playing song"):
        song_name = action[len("playing song "):].strip()
        if song_name:
            success = play_song_on_youtube(song_name)
            if not success:
                speak("I couldn't play the song on YouTube.")
        else:
            logging.warning("Song name not specified for 'playing song' command.")
            speak("Please specify the song name to play on YouTube.")
        return

    elif action.startswith("sending ") and " to " in action and " on whatsapp" in action:
        try:
            pattern = r"^sending\s+(.*?)\s+to\s+(.*?)\s+on whatsapp$"
            match = re.match(pattern, action)
            if match:
                message = match.group(1).strip()
                contact_name = match.group(2).strip()
                if message and contact_name:
                    send_whatsapp_message(contact_name, message)
                else:
                    logging.warning("Message or contact name is missing for 'sending ... to ... on whatsapp' command.")
                    speak("Message or contact name is missing.")
            else:
                logging.warning("Failed to parse 'sending ... to ... on whatsapp' command.")
                speak("I couldn't understand the WhatsApp message command.")
        except Exception as e:
            logging.error(f"Error processing WhatsApp message command: {e}")
            speak("An error occurred while trying to send the WhatsApp message.")
        return

    else:
        # Handle other potential actions or remain silent
        logging.warning(f"Unrecognized automation action: '{action}'")
      
        return

# -------------------- Start Reminder Checking Thread --------------------
def start_reminder_checker():
    reminder_thread = threading.Thread(target=check_reminders, daemon=True)
    reminder_thread.start()
    logging.info("Started reminder checker thread.")

# -------------------- Initialize Background Music --------------------
def initialize_background_music():
    """
    Initializes and starts background music.
    """
    try:
        mixer.init()
        mixer.music.load(BACKGROUND_MUSIC_FILE)
        mixer.music.play(-1)  # Play on loop
        logging.info("Background music started.")
    except Exception as e:
        logging.error(f"Error initializing background music: {e}")
        speak("An error occurred while initializing background music.")

# -------------------- Main Execution --------------------
def main():
    """
    Main function to initialize automation tasks.
    """
    logging.info("Automation script started.")
    initialize_background_music()
    start_reminder_checker()
    # The rest of your automation tasks can be initialized here or handled externally.

if __name__ == "__main__":
    main()

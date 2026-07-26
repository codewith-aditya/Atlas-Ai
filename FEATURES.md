# 🌟 ATLAS - AI Personal Assistant: Feature Capabilities

Atlas is not just a chatbot; it is an advanced, fully-fledged desktop assistant with deep OS hooks, cognitive processing, and sensory awareness. Below is a comprehensive list of its core technical features, commands, and capabilities.

---

## 💻 1. Operating System Automation & Execution
Atlas understands conversational commands and maps them directly to Windows OS operations.
- **Application Control:** Say `"Open Notepad"` or `"Close Calculator"`. Atlas uses Windows shell commands and process iteration (`psutil`) to seamlessly launch or forcefully terminate applications. Smart matching ensures slight phrase variations work perfectly.
- **Tab & Window Management:** Command `"Close YouTube"`. Atlas scans all active window titles via `pygetwindow`, brings the target window to the foreground, and simulates the `Ctrl+W` macro to kill specific tabs without closing the entire browser.
- **Hardware Integration:** `"Increase brightness by 25%"` or `"Decrease volume"`. Atlas interfaces directly with Windows APIs (`screen_brightness_control`) and system volume settings.
- **Search & Navigation:** `"Search for Python tutorials on Google"` or `"Open latest news"`. Atlas constructs proper URL queries and launches the default browser automatically.
- **Self-Cleaning:** Command `"Cleaning initializing"` to have Atlas automatically close unwanted background processes and free up system memory instantly.

## 🧠 2. Cognitive AI Brain (`Ai.py`)
Atlas processes everything you say through an advanced neural pipeline before responding.
- **Emotion Engine & Empathy:** Analyzes your text (e.g., "I'm so angry right now" vs "This is awesome!"). It maps this to a sentiment vector (Joy, Anger, Frustration, Urgency) and dynamically alters its response tone, automatically prepending empathetic phrases before executing tasks.
- **Persistent Context Memory:** Atlas remembers details about you (your name, city, interests) and past conversational context, stored safely in `context_memory.json`. It uses a rolling window and TF-IDF similarity to recall past events during a chat.
- **Pattern & Routine Learning:** Tracks command frequencies. If you check the weather every morning, Atlas logs this in `user_patterns.json` and begins to proactively suggest the action.

## 🎙️ 3. Seamless Voice Pipeline
Atlas uses a custom audio pipeline designed for natural, zero-latency interactions.
- **Dynamic Listening (`listening.py`):** Automatically calibrates to the ambient noise level of your room. It features an extended 8-second timeout threshold, meaning you can pause to think mid-sentence without Atlas abruptly cutting you off.
- **Zero-Latency TTS (`speech_windows.py`):** Atlas bypasses slow cloud APIs and leverages a hidden Windows PowerShell process (System.Speech.Synthesis) to speak instantly with 0ms latency, using the built-in Microsoft David voice.

## 👁️ 4. Vision & Sensory Modules
Atlas has "eyes" and can interact with the physical and digital world.
- **Webcam Interface:** Command `"Open camera"` or `"Close camera"` to toggle your local webcam feed.
- **Visual Scanning:** Command `"Visual scanning"` to have Atlas take a picture using your webcam. The image is passed to a multimodal LLM to describe objects, text, or people in your physical room.
- **Screen Reading:** Atlas can capture and interpret UI elements currently displayed on your monitor (`"What are you seeing?"`).

## 🎨 5. Sci-Fi UI & Dashboard
The visual interface is designed to look like a high-tech command center.
- **Sleek Dark Theme:** Eye-friendly dark interface built on PyQt5, using frameless, transparent windows and glowing CSS elements (Electric Cyan & Neon Green).
- **Real-Time Telemetry:** Displays live graphs and percentages for CPU load, RAM usage, and Disk space.
- **Interactive Chat Panel:** A scrollable messaging interface that logs voice commands and allows silent text input.
- **Background Ambiance:** Optional background sci-fi music (`brain_power_music.mp3`) that can be toggled via voice commands while working.

## 🛡️ 6. Identity Enforcement & Security
- **Strict Persona:** Atlas is heavily sandboxed by its system prompt (`system.initialize`). It will always assert itself as "Atlas, the assistant created by Aditya."
- **Encrypted Boot Sequence:** The system uses symmetric encryption to validate and lock your subscription key to your machine. Without a valid, unexpired key, the AI brain cannot boot.
- **Data Storage:** All user memory, patterns, and context data are stored **locally** on your machine. No cloud uploads (except secure API calls to the LLM backend).

---

## 🗣️ Voice Commands Reference

### Basic Commands
- `"Hello Atlas"` - Greet and start a conversation.
- `"What time is it?"` / `"checking time"` - Get the current time.
- `"What's the weather?"` / `"checking weather"` - Get a weather update for your city.
- `"Good night Atlas"` - End conversation.

### Application & Window Control
- `"Open YouTube"` - Opens YouTube in the browser.
- `"Open Notepad"` - Opens Notepad.
- `"Open [app name]"` - Searches and opens a specific application.
- `"Close YouTube"` - Closes the YouTube tab.
- `"Close [app name]"` - Closes a specific application.

### System Control
- `"Increase volume"` / `"Decrease volume"` - Adjusts system audio by 10%.
- `"Increase volume by [X]%"` - Adjusts volume by an exact percentage.
- `"Increase brightness"` / `"Decrease brightness"` - Adjusts screen brightness.

### Vision & Sensory
- `"What are you seeing?"` - Analyzes current screen.
- `"Visual scanning"` - Scans and describes content via webcam.
- `"Opening camera"` / `"Closing camera"` - Toggles the webcam.

### Automation
- `"Search for [query] on Google"` - Google web search.
- `"Opening latest news"` - Opens recent news.
- `"Background music turning on"` / `"Background music turning off"` - Toggles ambient music.
- `"Cleaning initializing"` - Closes unnecessary processes.
- `"Reminder set for [time]"` - Schedules a reminder.
- `"#writing [topic]"` - Generates content and automatically writes it directly into Notepad.

---

## 🛠️ Technical Specifications

### Core Technologies
- **Language:** Python 3.13
- **GUI Framework:** PyQt5
- **Speech Recognition:** Google Speech Recognition
- **Text-to-Speech:** Windows SAPI (PowerShell `System.Speech.Synthesis`)
- **AI Models:** Groq (`llama-3.1-8b-instant`), Google Gemini
- **Audio:** `pygame` mixer
- **Encryption:** `cryptography.fernet`

### System Requirements
- **OS:** Windows 10/11
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB free space
- **Microphone & Speakers:** Required for voice I/O
- **Internet:** Required for AI and speech recognition
## 🎤 Voice Interaction
- **Smart Voice Recognition** - Advanced speech-to-text with Google Speech Recognition
- **Smart Calibration** - Automatically adjusts to your voice to prevent self-listening
- **Natural Conversations** - Powered by Groq AI for human-like responses
- **Text-to-Speech** - Clear, natural voice output using Windows TTS

### 🧠 Artificial Intelligence
- **Conversational AI** - Context-aware conversations with memory
- **Learning & Memory** - Remembers your preferences and past interactions
- **Pattern Recognition** - Learns from your usage patterns
- **Multi-AI Support** - Groq, Gemini, and GPT integration

### 🤖 Automation & Control
- **Application Control** - Open, close, and manage applications
- **Web Automation** - Search Google, open websites, control browser
- **System Control** - Adjust volume, brightness, system settings
- **File Management** - Create, move, delete files and folders
- **Window Management** - Switch between windows, close tabs

### 📸 Vision & Analysis
- **Screen Analysis** - Analyze what's on your screen using Gemini Vision
- **Image Recognition** - Understand and describe images
- **Visual Scanning** - "What are you seeing?" command support

### 🎯 Smart Features
- **Auto-Startup** - Starts automatically with Windows
- **Background Music** - Optional ambient music while working
- **System Monitoring** - CPU, RAM, battery status display
- **Weather Updates** - Get current weather for your city
- **Time & Date** - Quick time and date queries

### 💾 Memory & Learning
- **Conversation History** - Saves all your conversations
- **User Preferences** - Remembers your settings and choices
- **Context Awareness** - Understands conversation context
- **Pattern Learning** - Adapts to your usage patterns

---

## 🎨 User Interface

### Modern GUI
- **Sleek Dark Theme** - Eye-friendly dark interface
- **Real-time Metrics** - CPU, RAM, battery monitoring
- **Animated Elements** - Smooth animations and transitions
- **System Tray** - Minimize to system tray
- **Always on Top** - Optional always-on-top mode

### Visual Feedback
- **Voice Indicator** - Shows when listening/speaking
- **Status Updates** - Real-time status messages
- **Response Display** - Shows AI responses in GUI

---

## 🗣️ Voice Commands

### Basic Commands
---

## 🔐 Privacy & Security

### Data Storage
- ✅ All contextual data and user patterns are stored locally.
- ✅ No cloud uploads for personal files.
- ✅ Encrypted API and subscription keys.
- ✅ User privacy strictly protected.

### API Usage
- **Groq AI** - Ultra-fast conversation and task processing.
- **Google Gemini** - Vision and advanced AI analysis.
- **Google Speech** - Voice-to-text recognition.
- **OpenWeatherMap** - Live weather data.

---

## 🆕 Upcoming Features

### In Development
- 👩 **Aria** - Female AI assistant version.
- 🎙️ **ElevenLabs** - Premium, ultra-realistic voice quality.
- 🏠 **IoT Control** - Smart home automation integration.
- 🌐 **LiveKit** - Enhanced voice streaming and low-latency interaction.
- 📱 **Mobile App** - Android/iOS companion application.

### Planned
- Multi-language support (Hindi support in progress).
- Custom wake words.
- Plugin system.
- Cloud sync (optional).
- Team collaboration features.

---

## 💰 Pricing & Licensing

### Personal Use
- **Source Code:** ₹25,000 - ₹35,000
- **Includes:** Full source, documentation, updates (30 days)
- **License:** Single user, non-commercial

### Commercial Use
- **Small Business:** ₹50,000 - ₹1,00,000
- **Enterprise:** ₹2,00,000+
- **Includes:** Custom branding, priority support, dedicated updates

### Add-ons
- **Female version (Aria):** +₹10,000
- **ElevenLabs voice integration:** +₹5,000
- **Custom features:** Quote-based
- **Extended support:** ₹5,000/month

---

## 👨‍💻 Developer & Support

**Created by:** Aditya Wakharkar  
**Email:** adityawakharkar99@gmail.com  
**WhatsApp:** +91 9309039729  
**Version:** 1.0 - Production Ready  
**Status:** ✅ Active Development

**License:**  
**Private Project** - All rights reserved. Unauthorized distribution prohibited.  

For queries, customization, or support, please reach out via Email or WhatsApp. (Response Time: 24-48 hours)

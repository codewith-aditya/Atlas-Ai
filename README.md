<div align="center">

# 🤖 ATLAS AI

### Your Advanced Personal Desktop Assistant — Local, Sci-Fi, and Deeply OS-Integrated

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/GUI-PyQt5-brightgreen.svg?style=for-the-badge" alt="GUI">
  <img src="https://img.shields.io/badge/AI-Groq-orange.svg?style=for-the-badge" alt="AI Backend">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6.svg?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
</p>

<p>
  <img src="https://img.shields.io/github/stars/codewith-aditya/Atlas-Ai?style=social" alt="Stars">
  <img src="https://img.shields.io/github/forks/codewith-aditya/Atlas-Ai?style=social" alt="Forks">
  <img src="https://img.shields.io/github/last-commit/codewith-aditya/Atlas-Ai?color=blue" alt="Last Commit">
</p>

**A sci-fi "Jarvis" for your desktop — one that listens, sees, remembers, and actually controls your machine.**

[Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#️-system-architecture) • [Auth System](#-the-key--authentication-system) • [Contributing](#-contributing)

</div>

---

## 🌌 What is Atlas?

Most "AI assistants" are chatbots wearing a nice UI. **Atlas is not that.**

It's a locally-run Python assistant that sits *inside* your operating system — not beside it. Ask it to open an app, mute your volume, describe what's on your screen, or just vent about your day, and it responds with zero-latency voice, real system telemetry, and a memory that persists across sessions. Built with a holographic "Astra" aesthetic, Atlas feels less like software and more like a presence on your desktop.

If you've ever wanted your PC to feel like it's *listening* — this is that project.

<p align="center">
  <img src="materials/img/screenshot_1.png" width="48%">
  <img src="materials/img/screenshot_2.png" width="48%">
</p>
<p align="center">
  <img src="materials/img/screenshot_3.png" width="48%">
  <img src="materials/img/screenshot_4.png" width="48%">
</p>

---

## ✨ Key Features

| Category | What It Does |
|---|---|
| 🖥️ **OS Control** | Open/close apps, manage windows & tabs, adjust volume/brightness — all via natural language |
| 🧠 **Cognitive Brain** | Emotion detection, persistent cross-session memory, and pattern learning that adapts to you |
| 🎙️ **Zero-Latency Voice** | Local Windows SAPI/PowerShell TTS for instant replies + ambient noise calibration so it hears you properly |
| 👁️ **Vision** | Webcam-based environment analysis and screen reading — Atlas can *see* what you see |
| 📊 **Live Sci-Fi Dashboard** | Frameless PyQt5 HUD with real-time CPU/RAM/Disk telemetry and holographic feedback |

> 📖 Want the full breakdown, module-by-module? See **[FEATURES.md](./FEATURES.md)**.

---

## 🚀 Quick Start

### Prerequisites
- Python **3.10+**
- Windows (for native TTS/SAPI support)
- A free [Groq API key](https://console.groq.com/)

### 1. Clone the Repository
```bash
git clone https://github.com/codewith-aditya/Atlas-Ai.git
cd Atlas-Ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
# Rename and edit the env file with your Groq key
cp .env.example .env

# Add your OpenWeatherMap key
cd materials/
cp weather_api_key.txt.example weather_api_key.txt
```

### 4. Launch Atlas
```bash
python main.py
```

> 💡 **First launch:** The GUI will prompt for a subscription key. This is the open-source release — use `atlas-lifetime-master` to unlock full access. See the [authentication section](#-the-key--authentication-system) below for how this works under the hood.

---

## 🏗️ System Architecture

Atlas isn't one script — it's a modular nervous system where each file has a clear job:

```
Atlas-Ai/
├── main.py              # 🧠 Nervous System — boot, GUI init, threading, query routing
├── automation.py         # 🦾 The Hands — OS ops via psutil, pyautogui, subprocess
├── Ai.py                 # 💭 The Brain — emotion detection, TF-IDF contextual memory
├── conversational_ai.py  # 🗣️ The Voice — Groq/LLM connection, persona enforcement
├── listening.py          # 👂 The Ears — ambient-aware microphone input
├── speech_windows.py      # 🔊 The Mouth — zero-latency Windows SAPI output
└── Gui.py                # 👤 The Face — frameless sci-fi HUD, live telemetry
```

| Module | Role | Key Libraries |
|---|---|---|
| `main.py` | Boots the app, wires up threads, routes every query to the right module | `PyQt5`, `threading` |
| `automation.py` | Turns LLM intent into real OS actions | `psutil`, `pyautogui`, `subprocess` |
| `Ai.py` | Detects emotion, injects empathy, recalls relevant memory | `scikit-learn` (TF-IDF) |
| `conversational_ai.py` | Talks to Groq, keeps Atlas in-character | `groq` |
| `listening.py` | Calibrates to ambient noise, captures speech | `speech_recognition`, `pyaudio` |
| `speech_windows.py` | Converts text to speech instantly, no cloud round-trip | Windows SAPI / PowerShell |
| `Gui.py` | Renders the live dashboard | `PyQt5` |

---

## 🔑 The Key & Authentication System

Atlas ships with a lightweight local licensing layer. Here's exactly how it works:

1. **Prompt on first boot** — `main.py` launches a PyQt5 `SubscriptionGUI` asking for a key.
2. **Key tiers:**

   | Key | Access Duration |
   |---|---|
   | `atlas-testing-key` | 5 minutes |
   | `atlas-weekly-pro` | 7 days |
   | `atlas-monthly-elite` | 30 days |
   | `atlas-lifetime-master` | Unlimited |

3. **Validation & encryption** — the entered key is checked against an internal dictionary; if valid, an expiration timestamp is calculated, encrypted with a symmetric `Fernet` key, and written to `materials/system.cfg`.
4. **Boot check** — on every subsequent launch, `main.py` decrypts `system.cfg`. Valid timestamp → Atlas boots straight through. Expired → the config is deleted and the prompt reappears.
5. **LLM auth passthrough** — the raw key is also stored in `materials/recover.txt` and reused as the API key for the Groq backend.

> ⚠️ **Heads-up for contributors:** since this is open-source, the key dictionary and Fernet secret live in the codebase itself — meaning the gate is more of a UX formality than a real restriction in this public build. If you're forking this for a distributed/commercial version, you'll want to move key validation server-side.

---

## 🤝 Contributing

PRs are genuinely welcome — automation hooks, UI polish, new model integrations, all fair game.

1. Fork the repo
2. Create a branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

Licensed under the **MIT License** — see [LICENSE](./LICENSE) for details.

---

<div align="center">

## 👨‍💻 Developer

**Aditya Wakharkar**

📧 adityawakharkar

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/aditya-wakharkar-29ab10321/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/codewith-aditya/)

**Status:** 🟢 Active Development

</div>

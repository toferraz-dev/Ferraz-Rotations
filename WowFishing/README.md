<div align="center">
  <img src="https://raw.githubusercontent.com/toferraz-dev/Ferraz-Rotations/main/WowFishing/src/icon.png" width="128" height="128" alt="Ferraz FW Icon">
  <h1>🎣 Ferraz FW (WoW Auto-Fisher)</h1>
  <p><strong>An advanced, autonomous, and highly optimized fishing bot for World of Warcraft, disguised under a modern interface.</strong></p>
</div>

---

## ✨ Features and Implementations

### 🛡️ Security & Anti-Detection Focus
- **Process Disguise (Stealth):** The bot runs under the name and icon of **Discord**. It binds to the Discord AppID and only allows execution if the real Discord application is already running on the PC.
- **Human-like Movement (Bézier):** The cursor doesn't "teleport." It uses Bézier curves and advanced Gaussian delays (mathematical bell-curve randomness) to simulate the imperfect movement of a human wrist.
- **Dynamic Anti-AFK Mechanics:** Features random jumps (`Space`) every 13-18 minutes, micro camera movements between casts, and randomized pauses ("Micro AFKs" of 5-20s or "Long AFKs" simulating bathroom breaks).
- **Native HID Hardware Support:** The source code contains templates and scripts (`FerrazHID`) for native USB communication with an **Arduino Pro Micro (ATmega32u4)**, transferring mouse and keyboard actions 100% via hardware.

### 🎨 New Graphical Interface ("AutoFish" Style)
The bot underwent a complete redesign using `CustomTkinter`. The current interface focuses on practicality and a modern Dark Mode aesthetic, featuring:
- **Compact Panel Layout** dividing *Fishing Settings*, *Detection (Computer Vision)*, and *Logs*.
- **Intuitive Visual Calibration:** A dedicated "Calibrate Fishing Zone" button to physically select the water area and the color sampling (HSV) of the bait.
- **Precision "Auto" Buttons:** Sensitive sliders (Sensitivity, Area, Tolerance) contain auto-configuration shortcuts to restore recommended defaults.
- **"Advanced Settings" Window (Pop-up):** Settings like Themes, Discord Webhooks, System Tray toggles, and Session History are hidden in a secondary window to keep the main panel clean.

### 🔔 Deep Discord Integration
- **Real-Time Webhook Notifications:** Sends Rich Embedded messages directly to your Discord server with Status Updates, Bot Timers, Bugs/Failsafes, `Catch Rate%`, and Session Summaries.

### 🤖 Complete Mechanical Automation
- Secondary bait automation (Auto-Bait) every X minutes.
- Auto-stop `Timer` for safe, unattended sessions.
- Visual Bobber Recognition using adaptive thresholds via **OpenCV/Numpy**. The bot actively monitors frames and counts real "splashes" before hooking.
- Cross-thread screen resolution via optimized, dynamic `mss` contexts.

### 🔐 Licensing and Update System (OTA)
- **Supabase Cloud:** Verifies and registers access keys tied to expiration dates in the cloud, using background REST_RPC requests without freezing the app.
- **Built-in Auto-Updater:** On every boot, it passively pings GitHub to verify the version (if outdated, displays an overlay for a safe patch download).

---

## 🚀 How to Build the Executable (Nuitka)

The project migrated from PyInstaller to the powerful **Nuitka**, which converts Python code directly to native C (compiled via MSVC), drastically increasing the obfuscation factor against reverse engineering (Anti-Cheat).

1. Ensure you have **MSVC 14.5** (Visual Studio Build Tools) and Python > 3.10 installed.
2. In the `/src` folder, double-click:
   ```cmd
   Build_Executable.bat
   ```
3. The script will install dependencies (`ordered-set`, `zstandard`), package images (icons) with the `tk-inter` engine, compress the Payload (~73%), and create a shielded `Ferraz FW.exe` file in the project directory.

---

## 🎮 Quick Start Guide

1. Open **Discord** on your PC (Mandatory to bypass the Stealth `mutex` lock).
2. Open `Ferraz FW.exe`. Log in with your Valid License (if prompted).
3. **Fishing Settings:** Set your in-game Fishing Macro shortcut in the main `Fishing Key` panel, and configure essential shortcuts like `Bait` and Stop/Pause keys.
4. **Calibrate:** Click **Calibrate Fishing Zone**. Drag your mouse over the water area (click, hold, drag, and release). Then click exactly on the red part of the bobber.
5. Click the **START** button! The bot will do a 5-second countdown. Maximize WoW and let it work silently.

---

*(Private Dev Note: This project contains injection and hardware utilities. Never distribute the `/Arduino/FerrazHID` folder in public builds if you intend to keep the FUD [Fully Undetectable] bypass vector exclusive.)*

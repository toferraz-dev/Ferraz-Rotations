# 🎣 Ferraz Fishing

Automated fishing for World of Warcraft using pixel analysis and a sleek Dark Mode GUI.

## How it Works

The bot takes screenshots of the region around the bobber at high frequency (~20fps) and compares consecutive frames. When the bobber splashes (moves), the difference between frames exceeds the configured threshold, and the bot automatically right-clicks. It does NOT inject into the game or read memory.

## Features

- **Modern Dark Mode UI:** Everything is managed through a beautiful, sleek interface.
- **Visual Auto-Calibration:** Easily drag and drop to select your fishing area and click the bobber's feather to lock its color.
- **Live Dashboard:** Watch your *Casts* and *Catches* update in real-time right on the screen.
- **Auto-Updater:** A single click updates the bot straight from GitHub!
- **Failsafes & Shortcuts:** Instantly pause with `[F9]`, stop with `[F8]`, or slam your mouse to the top-left corner to trigger the emergency stop.

## Installation & Usage

1. Enter WoW in **Windowed** or **Windowed (Fullscreen)** mode.
2. Go to a spot with water and equip your fishing pole.
3. Double click the `FishGUI.bat` file to start the bot.
   *Note: If you don't have Python installed, our smart launcher will detect it and provide you with a pop-up to download it! (Remember to mark "Add Python to PATH" during installation).*
4. In the app, verify or change your **Fishing Keybind** (default: `"1"`).
5. Click **Calibrate Colors**: 
   - Drag a rectangle to define the search area.
   - Click exactly on your bobber's feather to lock the color (or press Enter for default).
6. Hit **Start Bot** and let it do the hard work!

## Controls & Shortcuts

- **Start/Stop Bot:** Click the button in the app, or press **F8** at any time.
- **Pause/Resume:** Press **F9** to pause/resume the bot temporarily without clearing calibration.
- **Emergency Stop:** Move the mouse quickly to the **top-left corner** of the screen (pyautogui failsafe).

## Settings Overview

| Parameter           | Default | Description                                                |
|---------------------|---------|------------------------------------------------------------|
| `Fishing Keybind`   | `"1"`   | WoW fishing keybind                                        |
| `Sensitivity`       | `35`    | Sensitivity slider (lower = more sensitive to movement)    |

*There are other advanced settings inside `wow_fisher_gui.py` if you wish to tweak timers and delays (`MAX_WAIT`, `RECAST_DELAY`, `CLICK_DELAY_MS` etc).*

## Tuning Tips

- **Clicking too early / false positives?** → Increase `Sensitivity` on the slider (try 45-60)
- **Not detecting the splash?** → Decrease `Sensitivity` on the slider (try 25-35)
- **Bobber gets lost before click?** → You might need to recalibrate the color in a different lighting.

## Notes

- The bot will request **Administrator** privileges automatically so the keyboard shortcuts work correctly even when you are focused on the game.
- WoW must be in **windowed** mode (not exclusive fullscreen) for the screen capture to work flawlessly.

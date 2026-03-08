# 🎣 WoW Fishing Bot

Automated fishing for World of Warcraft using pixel analysis.

## How it Works

The bot takes screenshots of the region around the bobber at high frequency (~20fps) and compares consecutive frames. When the bobber splashes (moves), the difference between frames exceeds the configured threshold, and the bot automatically right-clicks.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Open WoW in **Windowed** or **Windowed (Fullscreen)** mode.
2. Go to a spot with water and equip your fishing pole.
3. Configure the fishing keybind in the script (default: `"1"`).
4. Run the script **as Administrator** (required for the `keyboard` module to work):
   ```bash
   python wow_fisher.py
   ```
   *Alternatively, double click the `Fish.bat` file which will handle administrator elevation automatically.*
5. Follow the on-screen calibration instructions:
   - **Step 1:** Drag a rectangle to define the search area.
   - **Step 2:** Choose the default bobber color or precisely click on your bobber's feather color to configure its HSV values.
6. Done! The bot will cast and fish automatically.

## Stopping the Bot

- Press **F8** at any time.
- OR move the mouse quickly to the **top-left corner** of the screen (pyautogui failsafe).
- OR press **Ctrl+C** in the terminal.

## Pausing the Bot

- Press **F9** to pause/resume the bot.

## Settings (`wow_fisher.py`)

| Parameter           | Default | Description                                                |
|---------------------|---------|------------------------------------------------------------|
| `FISHING_KEY`       | `"1"`   | WoW fishing keybind                                        |
| `STOP_KEY`          | `"F8"`  | Key to stop the bot                                        |
| `PAUSE_KEY`         | `"F9"`  | Key to pause/resume the bot                                |
| `SENSITIVITY`       | `40`    | Sensitivity (lower = more sensitive to movement)           |
| `BOBBER_REGION_SIZE`| `90`    | Size of the monitored area in pixels                       |
| `MAX_WAIT`          | `28`    | Max time waiting for a fish before recasting (seconds)     |
| `RECAST_DELAY`      | `1.2`   | Delay after catching a fish to recast (seconds)            |
| `CLICK_DELAY_MS`    | `100`   | Delay between detecting a splash and clicking (ms)         |

## Tuning Tips

- **Clicking too early / false positives?** → Increase `SENSITIVITY` (try 45-60)
- **Not detecting the splash?** → Decrease `SENSITIVITY` (try 25-35)
- **Losing fishes?** → Decrease `CLICK_DELAY_MS`
- **Bobber gets lost before click?** → Adjust `HUE_TOLERANCE` / `SAT_TOLERANCE` / `VAL_TOLERANCE` or recalibrate the color

## Notes

- Run as **Administrator** so the `keyboard` module works correctly.
- WoW must be in **windowed** mode (not exclusive fullscreen).

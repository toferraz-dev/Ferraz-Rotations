Here is exactly how to use the WoW Fishing bot (`wow_fisher.py`), step-by-step:

### 1. Game Preparation
Before starting the script, you need to set up your game:
* **Window Mode**: Make sure World of Warcraft is running in **Windowed** or **Windowed (Fullscreen)** mode. Exclusive Fullscreen might not work properly with screen capture.
* **Keybind**: Place your Fishing spell on the **`1`** key on your action bar (this is the default key in the script, though you can edit `FISHING_KEY` inside `wow_fisher.py` to change it).
* **Position**: Stand near a body of water and face the direction you want to cast.

### 2. Starting the Bot
The easiest way to start the bot is to use the provided batch file:
* Navigate to your `WowFishing` folder.
* Double-click the **`Fish.bat`** file.
* **Note:** It will automatically ask for **Administrator privileges**. This is required for the bot to globally detect your keyboard inputs (like F8 to stop). It will also automatically check and install any missing Python libraries (`opencv-python`, `pyautogui`, etc.).

### 3. The Calibration Process (Very Important)
When the bot starts, it will guide you through a visual calibration process to tell it exactly where to look for the bobber. This prevents it from accidentally clicking on red objects in the background.

* If you have run it before, it might ask if you want to use your saved calibration. To re-do it, type `y` and press Enter.
* **Step 1 (Search Area):** The bot will take a screenshot and open it in fullscreen. **Click and drag a rectangle** around the area of water where your bobber usually lands. Make the box big enough to account for RNG casting angles, but small enough to exclude the ground/sky. Press **`ENTER`** to confirm your box.
* **Step 2 (Bobber Color):** The console will ask if you want to use the default color or calibrate a precise color.
  * **Press `ENTER`** to use the default color (which is tuned for the standard red/orange feather). This usually works perfectly.
  * *Optional:* If you type `c` and press Enter, you must first manually cast your line in-game, then a magnification screen will appear allowing you to click exactly on the pixel color of your specific bobber's feather.

### 4. Let it Fish
Once calibration is done, you don't need to do anything else!
1. The bot automatically presses `1` to cast.
2. It visually scans only inside the box you drew to find the bobber.
3. It moves your mouse exactly over the bobber.
4. It monitors the pixels right around the bobber. The exact moment the bobber "splashes" (pixel movement is detected), it automatically right-clicks.
5. It waits for the loot to process, and then casts again.

### 5. Bot Controls & Failsafes
You have full keyboard control while the bot is active:
* **Pause / Resume:** Press **`F9`** to pause the bot (for instance, if you need to reply to a whisper or clear out your bags), and press it again to resume.
* **Stop Bot:** Press **`F8`** to completely shut down the bot.
* **Emergency Failsafe:** If the bot goes crazy, throw your physical mouse extremely fast into the **top-left corner of your monitor**. This triggers `pyautogui`'s built-in killswitch and crashes the bot immediately.

"""
WoW Fishing Bot v3.0 - Bobber Detection with Configurable Area
=============================================================
Flow:
  1. Calibration: captures the screen and displays a window where you DRAG
     a rectangle to define the bobber search area.
  2. Casts the line (configurable key).
  3. Searches for the RED feather of the bobber ONLY within the defined area.
  4. Moves the mouse to the found bobber.
  5. Monitors for splash and right-clicks.
  6. Repeats.

Requirements:
    pip install pyautogui opencv-python numpy pillow keyboard

Press F8 to stop at any time.
Move the mouse to the top-left corner to trigger the failsafe.
"""

import time
import sys
import json
import threading
from pathlib import Path
import numpy as np
import cv2
import pyautogui
import keyboard
from PIL import ImageGrab

# ─── Settings ─────────────────────────────────────────────────────────────────

# WoW fishing key (change to your in-game keybind)
FISHING_KEY = "1"

# Key to stop the bot
STOP_KEY = "F8"

# Key to pause/resume the bot
PAUSE_KEY = "F9"

# Delay after casting before trying to find the bobber (seconds)
CAST_SETTLE_TIME = 2.5

# Maximum time to find the bobber inside the area (seconds)
FIND_BOBBER_TIMEOUT = 6.0

# After finding, wait for the bobber to settle down (seconds)
BOBBER_SETTLE_TIME = 1.0

# After catching, how long to wait before recasting (seconds)
RECAST_DELAY = 1.2

# Splash detection sensitivity (0-100). Lower = more sensitive.
SENSITIVITY = 35

# Size of the monitoring area around the bobber (pixels)
BOBBER_REGION_SIZE = 90

# Maximum time waiting for a fish before recasting (seconds)
MAX_WAIT = 28

# How many consecutive frames with movement to confirm a splash
CONFIRM_FRAMES = 2

# Delay before clicking after detecting a splash (ms)
CLICK_DELAY_MS = 100

# Show diff value on console every frame (useful for calibrating SENSITIVITY).
# Turn to True to see real-time numbers, turn off after calibrating.
SHOW_DIFF = True

# HSV tolerance around the clicked color (defined in calibration)
# HUE: ±15 degrees | SAT: -80 below clicked | VAL: -80 below clicked
HUE_TOLERANCE = 15
SAT_TOLERANCE = 80
VAL_TOLERANCE = 80

# Minimum area in px² to consider it as the bobber (filters out noise)
MIN_BOBBER_AREA = 30

# Default bobber color (OpenCV HSV) - calibrated from the WoW bobber
# Can be overridden by interactive calibration or saved file.
DEFAULT_BOBBER_HSV = (5, 244, 137)

# File where calibration is saved/loaded
CALIBRATION_FILE = Path(__file__).parent / "calibration.json"

# List of HSV ranges for detection (filled during calibration)
# Each item is (lower_np_array, upper_np_array)
BOBBER_COLOR_RANGES: list = []

# ─── Global Variables ─────────────────────────────────────────────────────────

running       = True
paused        = False
total_catches = 0
total_casts   = 0
start_time    = None

# Bobber search area: (left, top, right, bottom) in screen coordinates
search_region: tuple | None = None


# ─── Helper Functions ─────────────────────────────────────────────────────────

def log(msg: str, level: str = "INFO"):
    ts = time.strftime("%H:%M:%S")
    icons = {
        "INFO":  "ℹ ",
        "OK":    "✅",
        "WARN":  "⚠ ",
        "ERROR": "❌",
        "CAST":  "🎣",
        "CATCH": "🐟",
        "FIND":  "🔍",
    }
    icon = icons.get(level, "• ")
    print(f"[{ts}] {icon}  {msg}")


def stop_listener():
    global running
    keyboard.wait(STOP_KEY)
    running = False
    log(f"Bot stopped by user ({STOP_KEY} pressed).", "WARN")


def pause_listener():
    """Thread that toggles pause/resume on every PAUSE_KEY press."""
    global paused
    while running:
        keyboard.wait(PAUSE_KEY)
        if not running:
            break
        paused = not paused
        if paused:
            log(f"Bot PAUSED ({PAUSE_KEY}). Press {PAUSE_KEY} to resume.", "WARN")
        else:
            log(f"Bot RESUMED ({PAUSE_KEY}).", "OK")


def wait_if_paused():
    """Blocks while the bot is paused. Returns False if the bot is stopped."""
    while paused and running:
        time.sleep(0.2)
    return running


def grab_screen_region(region: tuple) -> np.ndarray:
    """Captures a screen region (left, top, right, bottom) → BGR numpy."""
    screenshot = ImageGrab.grab(bbox=region)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def grab_full_screen() -> np.ndarray:
    """Captures the entire screen → BGR numpy."""
    screenshot = ImageGrab.grab()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def get_monitor_region(cx: int, cy: int, size: int) -> tuple:
    """Returns (left, top, right, bottom) of a region centered at (cx, cy)."""
    half     = size // 2
    sw, sh   = pyautogui.size()
    return (
        max(0, cx - half),
        max(0, cy - half),
        min(sw, cx + half),
        min(sh, cy + half),
    )


def capture_region(region: tuple) -> np.ndarray:
    return grab_screen_region(region)


def compute_diff(frame1: np.ndarray, frame2: np.ndarray) -> float:
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    diff  = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 18, 255, cv2.THRESH_BINARY)
    return (np.count_nonzero(thresh) / thresh.size) * 100


# ─── Calibration: Bobber Color Picker ─────────────────────────────────────────

def hsv_to_ranges(h: int, s: int, v: int) -> list:
    """
    Given an HSV pixel (OpenCV scale: H 0-179, S 0-255, V 0-255),
    returns a list of (lower, upper) arrays with applied tolerance.
    Handles hue wrap-around at 0/179.
    """
    s_lo = max(0,   s - SAT_TOLERANCE)
    v_lo = max(0,   v - VAL_TOLERANCE)
    s_hi = 255
    v_hi = 255

    h_lo = h - HUE_TOLERANCE
    h_hi = h + HUE_TOLERANCE

    ranges = []
    if h_lo < 0:
        # Lower wrap: split into [0, h_hi] and [180+h_lo, 179]
        ranges.append((np.array([0,           s_lo, v_lo]),
                       np.array([h_hi,         s_hi, v_hi])))
        ranges.append((np.array([180 + h_lo,   s_lo, v_lo]),
                       np.array([179,           s_hi, v_hi])))
    elif h_hi > 179:
        # Upper wrap: split into [h_lo, 179] and [0, h_hi-180]
        ranges.append((np.array([h_lo,          s_lo, v_lo]),
                       np.array([179,            s_hi, v_hi])))
        ranges.append((np.array([0,             s_lo, v_lo]),
                       np.array([h_hi - 180,    s_hi, v_hi])))
    else:
        ranges.append((np.array([h_lo, s_lo, v_lo]),
                       np.array([h_hi, s_hi, v_hi])))
    return ranges


class ColorPicker:
    """
    Shows the captured screen in full screen.
    The user CLICKS on the bobber's feather color.
    Displays:
      - 6x Magnifier around the cursor (24x24 patch -> 144x144)
      - BGR and HSV values of the pixel under the cursor
      - Square showing the sampled color
    Returns the clicked HSV pixel or None if canceled.
    """
    WIN = "WoW Fishing Bot - Bobber Color"
    ZOOM = 6          # magnifier zoom factor
    PATCH = 24        # patch size (original image pixels)
    PANEL_H = 180     # height of bottom info panel

    def __init__(self, screenshot: np.ndarray):
        self.img      = screenshot.copy()
        self.display  = None
        self.mouse_x  = 0
        self.mouse_y  = 0
        self.clicked  = None   # (h, s, v) of clicked pixel
        self.done     = False

    def _get_pixel_hsv(self, x: int, y: int):
        """Returns (h, s, v) of pixel (x, y) on original BGR image."""
        h_img, w_img = self.img.shape[:2]
        px = max(0, min(w_img - 1, x))
        py = max(0, min(h_img - 1, y))
        bgr_pixel = self.img[py, px]
        hsv_img   = cv2.cvtColor(self.img[py:py+1, px:px+1], cv2.COLOR_BGR2HSV)
        h, s, v   = hsv_img[0, 0]
        return int(h), int(s), int(v), bgr_pixel

    def _draw(self):
        h_img, w_img = self.img.shape[:2]
        mx, my = self.mouse_x, self.mouse_y

        # Base: original image + top black bar
        disp = self.img.copy()
        cv2.rectangle(disp, (0, 0), (w_img, 56), (0, 0, 0), -1)
        cv2.putText(disp,
            "CLICK on the bobber feather color  |  ESC = cancel",
            (10, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 255), 2, cv2.LINE_AA)

        # Crosshair
        cv2.line(disp, (mx, 0),       (mx, h_img), (0, 220, 255), 1)
        cv2.line(disp, (0, my),       (w_img, my), (0, 220, 255), 1)
        cv2.circle(disp, (mx, my), 8, (0, 220, 255), 1)

        # ── Magnifier ─────────────────────────────────────────────────────────
        half  = self.PATCH // 2
        x1c   = max(0, mx - half)
        y1c   = max(0, my - half)
        x2c   = min(w_img, mx + half)
        y2c   = min(h_img, my + half)
        patch = self.img[y1c:y2c, x1c:x2c]

        zoom_w = self.PATCH * self.ZOOM
        zoom_h = self.PATCH * self.ZOOM
        if patch.size > 0:
            zoomed = cv2.resize(patch, (zoom_w, zoom_h), interpolation=cv2.INTER_NEAREST)
            # Centers magnifier top-right corner (with margin)
            margin = 70
            lx = w_img - zoom_w - margin
            ly = margin
            # Border
            cv2.rectangle(disp, (lx-2, ly-2), (lx+zoom_w+2, ly+zoom_h+2), (0,220,255), 2)
            disp[ly:ly+zoom_h, lx:lx+zoom_w] = zoomed
            # Center crosshair inside magnifier
            cx_z = lx + zoom_w // 2
            cy_z = ly + zoom_h // 2
            cv2.line(disp, (cx_z, ly),       (cx_z, ly+zoom_h), (0, 255, 0), 1)
            cv2.line(disp, (lx, cy_z),       (lx+zoom_w, cy_z), (0, 255, 0), 1)

        # ── Bottom left info panel ────────────────────────────────────────────
        h_v, s_v, v_v, bgr_px = self._get_pixel_hsv(mx, my)
        b, g, r = int(bgr_px[0]), int(bgr_px[1]), int(bgr_px[2])

        panel_y = h_img - self.PANEL_H
        cv2.rectangle(disp, (0, panel_y), (420, h_img), (20, 20, 20), -1)

        # Color square
        swatch_color = (int(b), int(g), int(r))
        cv2.rectangle(disp, (10, panel_y + 10), (80, panel_y + 80), swatch_color, -1)
        cv2.rectangle(disp, (10, panel_y + 10), (80, panel_y + 80), (200,200,200), 1)

        font  = cv2.FONT_HERSHEY_SIMPLEX
        lines = [
            f"BGR: ({b}, {g}, {r})",
            f"HSV: ({h_v}, {s_v}, {v_v})",
            "Click to use this color",
        ]
        for i, line in enumerate(lines):
            cv2.putText(disp, line, (95, panel_y + 32 + i * 28),
                        font, 0.7, (200, 220, 255), 1, cv2.LINE_AA)

        # Show confirm if clicked
        if self.clicked:
            ch, cs, cv_ = self.clicked
            cv2.putText(disp, f"Selected color: HSV ({ch},{cs},{cv_})",
                        (10, panel_y + 120),
                        font, 0.65, (0, 255, 90), 2, cv2.LINE_AA)
            cv2.putText(disp, "Press ENTER to confirm or click another color",
                        (10, panel_y + 152),
                        font, 0.55, (180, 180, 180), 1, cv2.LINE_AA)

        self.display = disp
        cv2.imshow(self.WIN, disp)

    def _mouse_cb(self, event, x, y, flags, param):
        self.mouse_x = x
        self.mouse_y = y
        if event == cv2.EVENT_LBUTTONDOWN:
            h, s, v, _ = self._get_pixel_hsv(x, y)
            self.clicked = (h, s, v)
            log(f"Sampled color: HSV=({h},{s},{v})", "OK")

    def run(self):
        """Returns (h, s, v) of the clicked pixel, or None if canceled."""
        cv2.namedWindow(self.WIN, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.WIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self.WIN, self._mouse_cb)

        while not self.done:
            self._draw()
            key = cv2.waitKey(20) & 0xFF
            if key == 13 and self.clicked:   # ENTER confirms
                self.done = True
            elif key == 27:                   # ESC cancels
                self.clicked = None
                self.done = True

        cv2.destroyAllWindows()
        return self.clicked


# ─── Calibration: Target Area Selection ───────────────────────────────────────

class RegionSelector:
    """
    Shows screenshot in fullscreen OpenCV window and lets user
    drag a rectangle to define the bobber search area.
    """

    def __init__(self, screenshot: np.ndarray):
        self.img        = screenshot.copy()
        self.display    = screenshot.copy()
        self.start_pt   = None
        self.end_pt     = None
        self.dragging   = False
        self.confirmed  = False

    def _draw(self):
        self.display = self.img.copy()
        h, w = self.display.shape[:2]

        # Top instructions
        cv2.rectangle(self.display, (0, 0), (w, 52), (0, 0, 0), -1)
        cv2.putText(self.display,
            "DRAG to define the bobber search area | ENTER = confirm | ESC = cancel",
            (10, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 180), 2, cv2.LINE_AA)

        if self.start_pt and self.end_pt:
            x1, y1 = self.start_pt
            x2, y2 = self.end_pt
            # Selection rect
            cv2.rectangle(self.display, (x1, y1), (x2, y2), (0, 255, 60), 2)
            # Semi-transparent overlay inside selection
            overlay = self.display.copy()
            cv2.rectangle(overlay,
                          (min(x1,x2), min(y1,y2)),
                          (max(x1,x2), max(y1,y2)),
                          (0, 255, 60), -1)
            cv2.addWeighted(overlay, 0.15, self.display, 0.85, 0, self.display)
            cv2.rectangle(self.display, (x1, y1), (x2, y2), (0, 255, 60), 2)

            # Dimensions
            rw  = abs(x2 - x1)
            rh  = abs(y2 - y1)
            txt = f"{rw} x {rh} px"
            cv2.putText(self.display, txt,
                        (min(x1,x2) + 4, min(y1,y2) - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 60), 2, cv2.LINE_AA)

        cv2.imshow("WoW Fishing Bot - Calibration", self.display)

    def _mouse_cb(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_pt  = (x, y)
            self.end_pt    = (x, y)
            self.dragging  = True
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.end_pt = (x, y)
            self._draw()
        elif event == cv2.EVENT_LBUTTONUP:
            self.end_pt   = (x, y)
            self.dragging = False
            self._draw()

    def run(self) -> tuple | None:
        """
        Opens calibration window and returns (left, top, right, bottom)
        in screen coordinates, or None if canceled.
        """
        cv2.namedWindow("WoW Fishing Bot - Calibration", cv2.WINDOW_NORMAL)
        # Fullscreen
        cv2.setWindowProperty("WoW Fishing Bot - Calibration",
                              cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("WoW Fishing Bot - Calibration", self._mouse_cb)
        self._draw()

        while True:
            key = cv2.waitKey(20) & 0xFF
            if key == 13:  # ENTER — confirm
                if self.start_pt and self.end_pt:
                    self.confirmed = True
                    break
            elif key == 27:  # ESC — cancel
                break
            self._draw()

        cv2.destroyAllWindows()

        if not self.confirmed or not self.start_pt or not self.end_pt:
            return None

        x1, y1 = self.start_pt
        x2, y2 = self.end_pt
        left   = min(x1, x2)
        top    = min(y1, y2)
        right  = max(x1, x2)
        bottom = max(y1, y2)

        if right - left < 20 or bottom - top < 20:
            return None  # Selection too small

        return (left, top, right, bottom)


# ─── Calibration Persistence ──────────────────────────────────────────────────

def save_calibration(region: tuple, hsv: tuple):
    """Saves region and HSV color in calibration.json."""
    data = {
        "region": list(region),
        "hsv":    list(hsv),
    }
    try:
        CALIBRATION_FILE.write_text(json.dumps(data, indent=2))
        log(f"Calibration saved at: {CALIBRATION_FILE.name}", "OK")
    except Exception as e:
        log(f"Could not save calibration: {e}", "WARN")


def load_calibration():
    """Loads saved calibration. Returns (region, hsv) or (None, None)."""
    if not CALIBRATION_FILE.exists():
        return None, None
    try:
        data   = json.loads(CALIBRATION_FILE.read_text())
        region = tuple(data["region"])
        hsv    = tuple(data["hsv"])
        log(f"Calibration loaded: region={region}  HSV={hsv}", "OK")
        return region, hsv
    except Exception as e:
        log(f"Error loading calibration: {e}", "WARN")
        return None, None


def calibrate() -> tuple:
    """
    Manages complete calibration:
      - If saved calibration exists, asks if wants to recalibrate.
      - If it doesn't exist (or you recalibrate), runs the 2 steps.
      - Always saves at the end.
    Returns (left, top, right, bottom) of the search area.
    """
    global BOBBER_COLOR_RANGES

    # ── Tries to load saved calibration ──────────────────────────────
    saved_region, saved_hsv = load_calibration()

    if saved_region and saved_hsv:
        print()
        print("  ┌──────────────────────────────────────────────────────────┐")
        print("  │  SAVED CALIBRATION FOUND                                 │")
        r = saved_region
        h, s, v = saved_hsv
        print(f"  │  Area: {r[0]},{r[1]} → {r[2]},{r[3]}  ({r[2]-r[0]}x{r[3]-r[1]}px){'':<12}│")
        print(f"  │  Bobber color: HSV=({h},{s},{v}){'':<30}│")
        print("  └──────────────────────────────────────────────────────────┘")
        print()
        resp = input("  Recalibrate? [y/N]: ").strip().lower()
        if resp != "y":
            BOBBER_COLOR_RANGES = hsv_to_ranges(*saved_hsv)
            log(f"Using saved calibration. HSV={saved_hsv}  Ranges={len(BOBBER_COLOR_RANGES)}", "OK")
            return saved_region

    # ── Full Calibration ──────────────────────────────────────────
    log("Capturing screen for calibration...", "INFO")
    time.sleep(0.5)
    screenshot = grab_full_screen()

    # Step 1: search area
    print()
    print("  ┌──────────────────────────────────────────────────────────┐")
    print("  │  STEP 1/2 — SEARCH AREA                                  │")
    print("  │  A window will open with your screen.                    │")
    print("  │  DRAG a rectangle over the WATER area                    │")
    print("  │  where the bobber will spawn.                            │")
    print("  │  ENTER = confirm selection   ESC = cancel                │")
    print("  └──────────────────────────────────────────────────────────┘")
    print()
    input("  Press ENTER to open the calibration window...")

    selector = RegionSelector(screenshot)
    region   = selector.run()
    if region is None:
        log("Calibration cancelled.", "ERROR")
        sys.exit(1)
    log(f"Search area: {region[2]-region[0]}x{region[3]-region[1]}px defined.", "OK")

    # Step 2: bobber color
    dh, ds, dv = DEFAULT_BOBBER_HSV
    print()
    print("  ┌──────────────────────────────────────────────────────────┐")
    print("  │  STEP 2/2 — BOBBER COLOR                                 │")
    print(f"  │  Default color: HSV=({dh},{ds},{dv}){'':<28}│")
    print("  │  Press ENTER to use the default color,                   │")
    print("  │  or 'c' + ENTER to click on the bobber to calibrate.     │")
    print("  └──────────────────────────────────────────────────────────┘")
    print()
    color_resp = input("  Choose [ENTER=default / c=calibrate]: ").strip().lower()

    chosen_hsv = DEFAULT_BOBBER_HSV
    if color_resp == "c":
        print()
        input("  Cast the line in WoW, minimize the game and press ENTER...")
        log("Capturing screen with the bobber...", "INFO")
        time.sleep(0.3)
        screenshot2 = grab_full_screen()
        picker = ColorPicker(screenshot2)
        result = picker.run()
        if result is None:
            log(f"Selection cancelled. Using default HSV={DEFAULT_BOBBER_HSV}.", "WARN")
        else:
            chosen_hsv = result
    else:
        log(f"Using default color: HSV={DEFAULT_BOBBER_HSV}", "INFO")

    BOBBER_COLOR_RANGES = hsv_to_ranges(*chosen_hsv)
    h, s, v = chosen_hsv
    log(f"Calibrated color: HSV=({h},{s},{v}) → {len(BOBBER_COLOR_RANGES)} range(s)", "OK")
    for lo, hi in BOBBER_COLOR_RANGES:
        log(f"   Range: {lo.tolist()} → {hi.tolist()}", "INFO")

    # Save for next session
    save_calibration(region, chosen_hsv)
    return region


# ─── Bobber Detection ─────────────────────────────────────────────────────────

def build_bobber_mask(hsv_img: np.ndarray) -> np.ndarray:
    """Builds the mask using user-calibrated ranges."""
    mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
    for lo, hi in BOBBER_COLOR_RANGES:
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv_img, lo, hi))
    kernel = np.ones((4, 4), np.uint8)
    return cv2.dilate(mask, kernel, iterations=2)


def find_bobber_in_image(bgr: np.ndarray, offset_x: int = 0, offset_y: int = 0):
    """
    Searches for the bobber's red feather in 'bgr'.
    Returns (screen_x, screen_y, area) or None.
    offset_x/y converts local image coordinates to screen coordinates.

    Uses the TOP of the red blob's bounding rect as a reference point,
    because the feather is at the top of the bobber.
    """
    hsv  = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = build_bobber_mask(hsv)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    area    = cv2.contourArea(largest)
    if area < MIN_BOBBER_AREA:
        return None

    # Bounding rect of the blob → uses horizontal center + vertical top
    bx, by, bw, bh = cv2.boundingRect(largest)
    lx = bx + bw // 2   # horizontal center of the blob
    ly = by              # top of the blob (where the feather is)
    return (lx + offset_x, ly + offset_y, area)


def find_bobber(search_area: tuple, timeout: float = FIND_BOBBER_TIMEOUT):
    """
    Repeatedly scans 'search_area' searching for the bobber.
    Returns (screen_x, screen_y) or None.
    """
    left, top, right, bottom = search_area
    log("Searching bobber in the search area...", "FIND")
    deadline = time.time() + timeout
    attempt  = 0

    while time.time() < deadline and running:
        attempt += 1
        region_img = grab_screen_region(search_area)
        result     = find_bobber_in_image(region_img, offset_x=left, offset_y=top)

        if result:
            sx, sy, area = result
            log(f"Bobber found at ({sx}, {sy}) | Area: {area:.0f}px² | Attempt {attempt}", "OK")
            return (sx, sy)

        if attempt % 6 == 0:
            elapsed = time.time() - (deadline - timeout)
            log(f"  Still searching... ({elapsed:.1f}s)", "INFO")
        time.sleep(0.15)

    log("Couldn't find the bobber in the selected area.", "WARN")
    return None


# ─── Fishing Functions ────────────────────────────────────────────────────────

def cast_fishing_line():
    global total_casts
    total_casts += 1
    log(f"Cast #{total_casts} — Pressing '{FISHING_KEY}'", "CAST")
    pyautogui.press(FISHING_KEY)
    log(f"Waiting {CAST_SETTLE_TIME}s for the bobber to land...", "INFO")
    time.sleep(CAST_SETTLE_TIME)


def move_to_bobber(bx: int, by: int):
    log(f"Moving mouse to ({bx}, {by})...", "INFO")
    pyautogui.moveTo(bx, by, duration=0.25)
    time.sleep(BOBBER_SETTLE_TIME)


# How many consecutive frames with diff≈0 before considering the bobber lost
# (only checked after the first second of monitoring)
LOST_BOBBER_FRAMES = 5


def wait_for_bite(region: tuple) -> bool:
    log("Monitoring splash...", "INFO")
    ref_frame        = capture_region(region)
    consecutive_hits = 0
    zero_frames      = 0      # consecutive frames with diff effectively 0
    elapsed          = 0.0
    interval         = 0.06

    while elapsed < MAX_WAIT and running:
        time.sleep(interval)
        elapsed  += interval
        new_frame = capture_region(region)
        diff_pct  = compute_diff(ref_frame, new_frame)

        # ── Pause ────────────────────────────────────────
        if paused:
            if SHOW_DIFF:
                print()
            if not wait_if_paused():
                return False
            # Restarts the reference frame after pausing
            ref_frame = capture_region(region)

        # ── Detect lost bobber (diff stuck at 0) ──────────────────────
        if elapsed > 1.0:  # ignores first second (bobber still settling)
            if diff_pct < 0.5:
                zero_frames += 1
                if zero_frames >= LOST_BOBBER_FRAMES:
                    if SHOW_DIFF:
                        print()
                    log("Diff zeroes - bobber lost or sunk. Recasting...", "WARN")
                    return False
            else:
                zero_frames = 0

        if SHOW_DIFF:
            bar_len = int(diff_pct)
            bar = "█" * min(bar_len, 60)
            marker = "◄ ABOVE THRESHOLD!" if diff_pct > SENSITIVITY else ""
            print(f"\r  diff={diff_pct:5.1f}% [{bar:<60}] {marker}   ", end="", flush=True)

        if diff_pct > SENSITIVITY:
            consecutive_hits += 1
            if not SHOW_DIFF:
                log(f"  Movement! diff={diff_pct:.1f}% ({consecutive_hits}/{CONFIRM_FRAMES})", "INFO")
            if consecutive_hits >= CONFIRM_FRAMES:
                if SHOW_DIFF:
                    print()  # breaks the bar line
                log(f"SPLASH confirmed! diff={diff_pct:.1f}%", "OK")
                return True
        else:
            if consecutive_hits > 0 and not SHOW_DIFF:
                log(f"  Signal cancelled (diff={diff_pct:.1f}%)", "INFO")
            consecutive_hits = 0
            ref_frame = cv2.addWeighted(ref_frame, 0.75, new_frame, 0.25, 0)

    if elapsed >= MAX_WAIT:
        log(f"Timeout after {MAX_WAIT}s — Recasting", "WARN")
    return False


def click_bobber(x: int, y: int):
    global total_catches
    time.sleep(CLICK_DELAY_MS / 1000)
    pyautogui.moveTo(x, y, duration=0.08)
    pyautogui.rightClick(x, y)
    total_catches += 1
    log(f"Fish #{total_catches} caught! 🐟", "CATCH")


def print_stats():
    elapsed = time.time() - start_time if start_time else 0
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    rate = (total_catches / (elapsed / 60)) if elapsed > 0 else 0
    print()
    print("═" * 45)
    print(f"  📊 SESSION STATISTICS")
    print(f"     Time        : {mins}m {secs}s")
    print(f"     Casts       : {total_casts}")
    print(f"     Catches     : {total_catches}")
    print(f"     Rate        : {rate:.1f} fish/min")
    print("═" * 45)


# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    global running, start_time, search_region

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE    = 0.04

    print()
    print("╔══════════════════════════════════════════════╗")
    print("║      🎣  WoW Fishing Bot  v3.0               ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  Fishing Key    : {FISHING_KEY:<27}║")
    print(f"║  Pause/Resume   : {PAUSE_KEY:<27}║")
    print(f"║  Stop Bot       : {STOP_KEY:<27}║")
    print(f"║  Sensitivity    : {SENSITIVITY:<27}║")
    print(f"║  Timeout        : {MAX_WAIT}s{'':<24}║")
    print("╠══════════════════════════════════════════════╣")
    print("║  ⚠  Mouse at top-left corner = failsafe     ║")
    print(f"║  ⚠  {PAUSE_KEY} = pause/resume{'':<21}║")
    print(f"║  ⚠  {STOP_KEY} = stop the bot{'':<22}║")
    print("╚══════════════════════════════════════════════╝")
    print()

    # 1. Calibration: defines search region
    search_region = calibrate()

    # 2. Start control threads
    stop_thread  = threading.Thread(target=stop_listener,  daemon=True)
    pause_thread = threading.Thread(target=pause_listener, daemon=True)
    stop_thread.start()
    pause_thread.start()

    start_time = time.time()
    log("Bot started! Casting the first time...", "INFO")
    print()

    try:
        while running:
            # Waits if paused
            if not wait_if_paused():
                break

            # Casts the line
            cast_fishing_line()
            if not running:
                break

            # Detects the bobber inside the configured area
            bobber = find_bobber(search_region)
            if not bobber:
                log("Bobber not found. Recasting in 2s...", "WARN")
                time.sleep(2.0)
                continue

            bx, by = bobber

            # Moves the mouse to the bobber
            move_to_bobber(bx, by)
            if not running:
                break

            # Monitors splash
            region        = get_monitor_region(bx, by, BOBBER_REGION_SIZE)
            bite_detected = wait_for_bite(region)

            # Clicks if detected
            if bite_detected and running:
                click_bobber(bx, by)
                time.sleep(RECAST_DELAY)

    except pyautogui.FailSafeException:
        log("FailSafe activated! Bot stopped.", "WARN")
    except KeyboardInterrupt:
        log("Interrupted (Ctrl+C).", "WARN")
    finally:
        running = False
        cv2.destroyAllWindows()
        print_stats()


if __name__ == "__main__":
    main()

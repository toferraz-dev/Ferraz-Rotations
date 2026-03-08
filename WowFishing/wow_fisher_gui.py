import time
import sys
import json
import threading
from pathlib import Path
import numpy as np
import cv2
import pyautogui
import keyboard
from PIL import ImageGrab, Image
import customtkinter as ctk
import ctypes
import subprocess

# ─── Settings ─────────────────────────────────────────────────────────────────
FISHING_KEY = "1"
STOP_KEY = "F8"
PAUSE_KEY = "F9"
CAST_SETTLE_TIME = 2.5
FIND_BOBBER_TIMEOUT = 6.0
BOBBER_SETTLE_TIME = 1.0
RECAST_DELAY = 1.2
SENSITIVITY = 35
BOBBER_REGION_SIZE = 90
MAX_WAIT = 28
CONFIRM_FRAMES = 2
CLICK_DELAY_MS = 100

HUE_TOLERANCE = 15
SAT_TOLERANCE = 80
VAL_TOLERANCE = 80
MIN_BOBBER_AREA = 30
DEFAULT_BOBBER_HSV = (5, 244, 137)

CALIBRATION_FILE = Path(__file__).parent / "calibration.json"
BOBBER_COLOR_RANGES: list = []

# Global Variables
running = False
paused = False
total_catches = 0
total_casts = 0
start_time = None
search_region = None

# GUI Reference
app = None

# ─── Helper Functions ─────────────────────────────────────────────────────────

def log(msg: str, level: str = "INFO"):
    ts = time.strftime("%H:%M:%S")
    icons = {
        "INFO":  "ℹ",
        "OK":    "✅",
        "WARN":  "⚠",
        "ERROR": "❌",
        "CAST":  "🎣",
        "CATCH": "🐟",
        "FIND":  "🔍",
    }
    icon = icons.get(level, "•")
    formatted_msg = f"[{ts}] {icon} {msg}\n"
    
    # Send safely to text box
    if app and app.log_box:
        app.log_box.after(0, app.append_log, formatted_msg)
    else:
        print(formatted_msg, end="")

def stop_listener():
    global running
    keyboard.wait(STOP_KEY)
    if running:
        running = False
        log(f"Bot stopped by user ({STOP_KEY} pressed).", "WARN")
        if app:
            app.after(0, app.update_ui_state)

def pause_listener():
    global paused
    while True:
        keyboard.wait(PAUSE_KEY)
        if not running:
            continue
        paused = not paused
        if paused:
            log(f"Bot PAUSED ({PAUSE_KEY}). Press {PAUSE_KEY} to resume.", "WARN")
        else:
            log(f"Bot RESUMED ({PAUSE_KEY}).", "OK")

def wait_if_paused():
    while paused and running:
        time.sleep(0.2)
    return running

def grab_screen_region(region: tuple) -> np.ndarray:
    screenshot = ImageGrab.grab(bbox=region)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def grab_full_screen() -> np.ndarray:
    screenshot = ImageGrab.grab()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def get_monitor_region(cx: int, cy: int, size: int) -> tuple:
    half = size // 2
    sw, sh = pyautogui.size()
    return (
        max(0, cx - half),
        max(0, cy - half),
        min(sw, cx + half),
        min(sh, cy + half),
    )

def compute_diff(frame1: np.ndarray, frame2: np.ndarray) -> float:
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    diff  = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 18, 255, cv2.THRESH_BINARY)
    return (np.count_nonzero(thresh) / thresh.size) * 100

def hsv_to_ranges(h: int, s: int, v: int) -> list:
    s_lo = max(0,   s - SAT_TOLERANCE)
    v_lo = max(0,   v - VAL_TOLERANCE)
    s_hi = 255
    v_hi = 255
    h_lo = h - HUE_TOLERANCE
    h_hi = h + HUE_TOLERANCE
    ranges = []
    if h_lo < 0:
        ranges.append((np.array([0,           s_lo, v_lo]),
                       np.array([h_hi,         s_hi, v_hi])))
        ranges.append((np.array([180 + h_lo,   s_lo, v_lo]),
                       np.array([179,           s_hi, v_hi])))
    elif h_hi > 179:
        ranges.append((np.array([h_lo,          s_lo, v_lo]),
                       np.array([179,            s_hi, v_hi])))
        ranges.append((np.array([0,             s_lo, v_lo]),
                       np.array([h_hi - 180,    s_hi, v_hi])))
    else:
        ranges.append((np.array([h_lo, s_lo, v_lo]),
                       np.array([h_hi, s_hi, v_hi])))
    return ranges

# ─── Calibration Tools ────────────────────────────────────────────────────────

class ColorPicker:
    WIN = "Ferraz Fishing - Bobber Color"
    ZOOM = 6
    PATCH = 24
    PANEL_H = 180

    def __init__(self, screenshot: np.ndarray):
        self.img = screenshot.copy()
        self.display = None
        self.mouse_x = 0
        self.mouse_y = 0
        self.clicked = None
        self.done = False

    def _get_pixel_hsv(self, x: int, y: int):
        h_img, w_img = self.img.shape[:2]
        px = max(0, min(w_img - 1, x))
        py = max(0, min(h_img - 1, y))
        bgr_pixel = self.img[py, px]
        hsv_img = cv2.cvtColor(self.img[py:py+1, px:px+1], cv2.COLOR_BGR2HSV)
        h, s, v = hsv_img[0, 0]
        return int(h), int(s), int(v), bgr_pixel

    def _draw(self):
        h_img, w_img = self.img.shape[:2]
        mx, my = self.mouse_x, self.mouse_y

        disp = self.img.copy()
        cv2.rectangle(disp, (0, 0), (w_img, 56), (0, 0, 0), -1)
        cv2.putText(disp, "CLICK on bobber feather | ESC = cancel | ENTER = use default",
                    (10, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 255), 2, cv2.LINE_AA)

        cv2.line(disp, (mx, 0), (mx, h_img), (0, 220, 255), 1)
        cv2.line(disp, (0, my), (w_img, my), (0, 220, 255), 1)
        cv2.circle(disp, (mx, my), 8, (0, 220, 255), 1)

        half = self.PATCH // 2
        x1c = max(0, mx - half)
        y1c = max(0, my - half)
        x2c = min(w_img, mx + half)
        y2c = min(h_img, my + half)
        patch = self.img[y1c:y2c, x1c:x2c]

        zoom_w = self.PATCH * self.ZOOM
        zoom_h = self.PATCH * self.ZOOM
        if patch.size > 0:
            zoomed = cv2.resize(patch, (zoom_w, zoom_h), interpolation=cv2.INTER_NEAREST)
            margin = 70
            lx = w_img - zoom_w - margin
            ly = margin
            cv2.rectangle(disp, (lx-2, ly-2), (lx+zoom_w+2, ly+zoom_h+2), (0,220,255), 2)
            disp[ly:ly+zoom_h, lx:lx+zoom_w] = zoomed
            cx_z = lx + zoom_w // 2
            cy_z = ly + zoom_h // 2
            cv2.line(disp, (cx_z, ly), (cx_z, ly+zoom_h), (0, 255, 0), 1)
            cv2.line(disp, (lx, cy_z), (lx+zoom_w, cy_z), (0, 255, 0), 1)

        h_v, s_v, v_v, bgr_px = self._get_pixel_hsv(mx, my)
        b, g, r = int(bgr_px[0]), int(bgr_px[1]), int(bgr_px[2])

        panel_y = h_img - self.PANEL_H
        cv2.rectangle(disp, (0, panel_y), (420, h_img), (20, 20, 20), -1)
        swatch_color = (int(b), int(g), int(r))
        cv2.rectangle(disp, (10, panel_y + 10), (80, panel_y + 80), swatch_color, -1)
        cv2.rectangle(disp, (10, panel_y + 10), (80, panel_y + 80), (200,200,200), 1)

        font  = cv2.FONT_HERSHEY_SIMPLEX
        lines = [f"BGR: ({b}, {g}, {r})", f"HSV: ({h_v}, {s_v}, {v_v})", "Click to use color"]
        for i, line in enumerate(lines):
            cv2.putText(disp, line, (95, panel_y + 32 + i * 28), font, 0.7, (200, 220, 255), 1)

        if self.clicked:
            ch, cs, cv_ = self.clicked
            cv2.putText(disp, f"Selected: HSV ({ch},{cs},{cv_})", (10, panel_y + 120), font, 0.65, (0, 255, 90), 2)
            cv2.putText(disp, "Press ENTER to confirm", (10, panel_y + 152), font, 0.55, (180, 180, 180), 1)

        self.display = disp
        cv2.imshow(self.WIN, disp)

    def _mouse_cb(self, event, x, y, flags, param):
        self.mouse_x = x
        self.mouse_y = y
        if event == cv2.EVENT_LBUTTONDOWN:
            h, s, v, _ = self._get_pixel_hsv(x, y)
            self.clicked = (h, s, v)

    def run(self):
        cv2.namedWindow(self.WIN, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.WIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self.WIN, self._mouse_cb)

        while not self.done:
            self._draw()
            key = cv2.waitKey(20) & 0xFF
            if key == 13:
                self.done = True
            elif key == 27:
                self.clicked = DEFAULT_BOBBER_HSV
                self.done = True

        cv2.destroyAllWindows()
        return self.clicked

class RegionSelector:
    def __init__(self, screenshot: np.ndarray):
        self.img = screenshot.copy()
        self.display = screenshot.copy()
        self.start_pt = None
        self.end_pt = None
        self.dragging = False
        self.confirmed = False

    def _draw(self):
        self.display = self.img.copy()
        h, w = self.display.shape[:2]
        cv2.rectangle(self.display, (0, 0), (w, 52), (0, 0, 0), -1)
        cv2.putText(self.display, "DRAG search area | ENTER = confirm | ESC = cancel",
                    (10, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 180), 2, cv2.LINE_AA)

        if self.start_pt and self.end_pt:
            x1, y1 = self.start_pt
            x2, y2 = self.end_pt
            cv2.rectangle(self.display, (x1, y1), (x2, y2), (0, 255, 60), 2)
            overlay = self.display.copy()
            cv2.rectangle(overlay, (min(x1,x2), min(y1,y2)), (max(x1,x2), max(y1,y2)), (0, 255, 60), -1)
            cv2.addWeighted(overlay, 0.15, self.display, 0.85, 0, self.display)
            cv2.rectangle(self.display, (x1, y1), (x2, y2), (0, 255, 60), 2)
            rw = abs(x2 - x1)
            rh = abs(y2 - y1)
            cv2.putText(self.display, f"{rw} x {rh} px", (min(x1,x2) + 4, min(y1,y2) - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 60), 2)

        cv2.imshow("Ferraz Fishing - Calibration", self.display)

    def _mouse_cb(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_pt = (x, y)
            self.end_pt = (x, y)
            self.dragging = True
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.end_pt = (x, y)
            self._draw()
        elif event == cv2.EVENT_LBUTTONUP:
            self.end_pt = (x, y)
            self.dragging = False
            self._draw()

    def run(self) -> tuple | None:
        cv2.namedWindow("Ferraz Fishing - Calibration", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Ferraz Fishing - Calibration", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("Ferraz Fishing - Calibration", self._mouse_cb)
        self._draw()

        while True:
            key = cv2.waitKey(20) & 0xFF
            if key == 13:
                if self.start_pt and self.end_pt:
                    self.confirmed = True
                    break
            elif key == 27:
                break
            self._draw()

        cv2.destroyAllWindows()
        if not self.confirmed or not self.start_pt or not self.end_pt:
            return None

        x1, y1 = self.start_pt
        x2, y2 = self.end_pt
        left, top = min(x1, x2), min(y1, y2)
        right, bottom = max(x1, x2), max(y1, y2)

        if right - left < 20 or bottom - top < 20:
            return None
        return (left, top, right, bottom)

# ─── Fishing Functions ────────────────────────────────────────────────────────

def build_bobber_mask(hsv_img: np.ndarray) -> np.ndarray:
    mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
    for lo, hi in BOBBER_COLOR_RANGES:
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv_img, lo, hi))
    kernel = np.ones((4, 4), np.uint8)
    return cv2.dilate(mask, kernel, iterations=2)

def find_bobber_in_image(bgr: np.ndarray, offset_x: int = 0, offset_y: int = 0):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = build_bobber_mask(hsv)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area < MIN_BOBBER_AREA:
        return None
    bx, by, bw, bh = cv2.boundingRect(largest)
    lx, ly = bx + bw // 2, by
    return (lx + offset_x, ly + offset_y, area)

def find_bobber(search_area: tuple, timeout: float = FIND_BOBBER_TIMEOUT):
    left, top, right, bottom = search_area
    log("Searching bobber...", "FIND")
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline and running:
        attempt += 1
        region_img = grab_screen_region(search_area)
        result = find_bobber_in_image(region_img, offset_x=left, offset_y=top)
        if result:
            sx, sy, area = result
            log(f"Bobber found! ({sx}, {sy}) [area:{area:.0f}]", "OK")
            return (sx, sy)
        time.sleep(0.15)
    log("Couldn't find the bobber.", "WARN")
    return None

def cast_fishing_line():
    global total_casts
    total_casts += 1
    log(f"Cast #{total_casts}", "CAST")
    pyautogui.press(FISHING_KEY)
    time.sleep(CAST_SETTLE_TIME)
    if app:
        app.after(0, app.update_stats)

def move_to_bobber(bx: int, by: int):
    pyautogui.moveTo(bx, by, duration=0.25)
    time.sleep(BOBBER_SETTLE_TIME)

def wait_for_bite(region: tuple) -> bool:
    log("Monitoring splash...", "INFO")
    ref_frame = capture_region(region)
    consecutive_hits = 0
    zero_frames = 0
    elapsed = 0.0
    interval = 0.06

    while elapsed < MAX_WAIT and running:
        time.sleep(interval)
        elapsed += interval
        new_frame = capture_region(region)
        diff_pct = compute_diff(ref_frame, new_frame)

        if paused:
            if not wait_if_paused():
                return False
            ref_frame = capture_region(region)

        if elapsed > 1.0:
            if diff_pct < 0.5:
                zero_frames += 1
                if zero_frames >= 5:
                    log("Bobber lost. Recasting...", "WARN")
                    return False
            else:
                zero_frames = 0

        if diff_pct > SENSITIVITY:
            consecutive_hits += 1
            if consecutive_hits >= CONFIRM_FRAMES:
                log(f"SPLASH confirmed! diff={diff_pct:.1f}%", "OK")
                return True
        else:
            consecutive_hits = 0
            ref_frame = cv2.addWeighted(ref_frame, 0.75, new_frame, 0.25, 0)

    return False

def click_bobber(x: int, y: int):
    global total_catches
    time.sleep(CLICK_DELAY_MS / 1000)
    pyautogui.moveTo(x, y, duration=0.08)
    pyautogui.rightClick(x, y)
    total_catches += 1
    log(f"Fish #{total_catches} caught! 🐟", "CATCH")
    if app:
        app.after(0, app.update_stats)

def bot_loop():
    global running, start_time
    start_time = time.time()
    try:
        while running:
            if not wait_if_paused():
                break

            cast_fishing_line()
            if not running: break

            bobber = find_bobber(search_region)
            if not bobber:
                time.sleep(2.0)
                continue

            bx, by = bobber
            move_to_bobber(bx, by)
            if not running: break

            region = get_monitor_region(bx, by, BOBBER_REGION_SIZE)
            bite_detected = wait_for_bite(region)

            if bite_detected and running:
                click_bobber(bx, by)
                time.sleep(RECAST_DELAY)

    except pyautogui.FailSafeException:
        log("FailSafe activated!", "ERROR")
    finally:
        running = False
        cv2.destroyAllWindows()
        log("Bot stopped.", "WARN")
        if app:
            app.after(0, app.update_ui_state)

# ─── GUI Application ──────────────────────────────────────────────────────────

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        global app
        app = self

        # Ensure Taskbar displays the icon properly
        try:
            myappid = 'wow.fisher.gui.v3'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        self.title("Ferraz Fishing")
        self.geometry("460x720")
        self.resizable(False, False)

        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        # Title and Image Icon
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=10)

        img_path = Path(__file__).parent / "icon.png"
        if img_path.exists():
            pil_image = Image.open(str(img_path))
            self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(48, 48))
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo_image, text="")
            self.logo_label.pack(side="left", padx=10)

        self.title_label = ctk.CTkLabel(self.header_frame, text="Ferraz Fishing", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left")

        # Settings Card
        self.settings_frame = ctk.CTkFrame(self, corner_radius=10)
        self.settings_frame.pack(pady=(5, 10), padx=20, fill="x")

        self.settings_title = ctk.CTkLabel(self.settings_frame, text="⚙️ Bot Configurations", font=ctk.CTkFont(size=16, weight="bold"))
        self.settings_title.grid(row=0, column=0, columnspan=3, pady=(15, 10), padx=15, sticky="w")

        self.key_label = ctk.CTkLabel(self.settings_frame, text="Fishing Keybind:", font=ctk.CTkFont(size=13))
        self.key_label.grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.key_entry = ctk.CTkEntry(self.settings_frame, width=70, justify="center")
        self.key_entry.insert(0, FISHING_KEY)
        self.key_entry.grid(row=1, column=1, columnspan=2, padx=15, pady=5, sticky="e")

        self.sens_label = ctk.CTkLabel(self.settings_frame, text="Sensitivity:", font=ctk.CTkFont(size=13))
        self.sens_label.grid(row=2, column=0, padx=15, pady=(5, 20), sticky="w")
        self.sens_slider = ctk.CTkSlider(self.settings_frame, from_=10, to=100, command=self.update_sens_label, button_color="#3498DB", button_hover_color="#2980B9")
        self.sens_slider.set(SENSITIVITY)
        self.sens_slider.grid(row=2, column=1, padx=5, pady=(5, 20))
        
        self.sens_val_label = ctk.CTkLabel(self.settings_frame, text=str(SENSITIVITY), font=ctk.CTkFont(weight="bold"))
        self.sens_val_label.grid(row=2, column=2, padx=(5, 15), pady=(5, 20))

        # Actions Frame
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(pady=5, padx=20, fill="x")

        self.calibrate_btn = ctk.CTkButton(self.actions_frame, text="Calibrate Colors", command=self.start_calibration, font=ctk.CTkFont(weight="bold"), fg_color="#E67E22", hover_color="#D35400", height=40)
        self.calibrate_btn.pack(side="left", padx=(0, 5), expand=True, fill="x")

        self.start_btn = ctk.CTkButton(self.actions_frame, text="Start Bot", command=self.toggle_bot, font=ctk.CTkFont(weight="bold"), fg_color="#27AE60", hover_color="#229954", height=40)
        self.start_btn.pack(side="left", padx=5, expand=True, fill="x")

        self.update_btn = ctk.CTkButton(self.actions_frame, text="Update", command=self.update_bot, width=70, font=ctk.CTkFont(weight="bold"), fg_color="#2980B9", hover_color="#1F618D", height=40)
        self.update_btn.pack(side="left", padx=(5, 0))

        # Legend
        self.legend_label = ctk.CTkLabel(self, text="⌨ Shortcuts: [F8] Stop Bot  |  [F9] Pause/Resume", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F1C40F")
        self.legend_label.pack(pady=(5, 10))

        # Stats Cards
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(pady=5, padx=20, fill="x")

        self.card_casts = ctk.CTkFrame(self.stats_frame, corner_radius=10)
        self.card_casts.pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkLabel(self.card_casts, text="🎣 CASTS", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(pady=(10, 0))
        self.casts_label = ctk.CTkLabel(self.card_casts, text="0", font=ctk.CTkFont(size=32, weight="bold"), text_color="#3498DB")
        self.casts_label.pack(pady=(0, 10))

        self.card_catches = ctk.CTkFrame(self.stats_frame, corner_radius=10)
        self.card_catches.pack(side="left", expand=True, fill="x", padx=(5, 0))
        ctk.CTkLabel(self.card_catches, text="🐟 CATCHES", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(pady=(10, 0))
        self.catches_label = ctk.CTkLabel(self.card_catches, text="0", font=ctk.CTkFont(size=32, weight="bold"), text_color="#2ECC71")
        self.catches_label.pack(pady=(0, 10))

        # Log Box
        self.log_box = ctk.CTkTextbox(self, state="disabled", wrap="word", height=180, corner_radius=10, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.pack(pady=(15, 20), padx=20, fill="both", expand=True)

        self.load_calibration_file()

        # Keyboard Threads
        threading.Thread(target=stop_listener, daemon=True).start()
        threading.Thread(target=pause_listener, daemon=True).start()

    def update_sens_label(self, val):
        self.sens_val_label.configure(text=str(int(val)))

    def append_log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def load_calibration_file(self):
        global search_region, BOBBER_COLOR_RANGES
        if CALIBRATION_FILE.exists():
            try:
                data = json.loads(CALIBRATION_FILE.read_text())
                search_region = tuple(data["region"])
                hsv = tuple(data["hsv"])
                BOBBER_COLOR_RANGES = hsv_to_ranges(*hsv)
                log(f"Loaded calibration. Area: {search_region[2]-search_region[0]}px", "OK")
            except Exception as e:
                log(f"Failed to load cal: {e}", "ERROR")

    def update_stats(self):
        self.casts_label.configure(text=str(total_casts))
        self.catches_label.configure(text=str(total_catches))

    def update_ui_state(self):
        if running:
            self.start_btn.configure(text="Stop Bot", fg_color="#C0392B", hover_color="#922B21")
            self.calibrate_btn.configure(state="disabled")
            self.key_entry.configure(state="disabled")
            self.sens_slider.configure(state="disabled")
        else:
            self.start_btn.configure(text="Start Bot", fg_color="#27AE60", hover_color="#229954")
            self.calibrate_btn.configure(state="normal")
            self.key_entry.configure(state="normal")
            self.sens_slider.configure(state="normal")

    def toggle_bot(self):
        global running, FISHING_KEY, SENSITIVITY
        if running:
            running = False
            log("Stopping bot...", "WARN")
            self.update_ui_state()
        else:
            if not search_region:
                log("Please calibrate first!", "ERROR")
                return
            
            FISHING_KEY = self.key_entry.get()
            SENSITIVITY = int(self.sens_slider.get())
            
            running = True
            self.update_ui_state()
            threading.Thread(target=bot_loop, daemon=True).start()

    def start_calibration(self):
        def _calib():
            global search_region, BOBBER_COLOR_RANGES
            log("Capturing screen for calibration...", "INFO")
            time.sleep(0.5)
            screenshot = grab_full_screen()
            
            selector = RegionSelector(screenshot)
            region = selector.run()
            if not region:
                log("Calibration cancelled.", "ERROR")
                return
            
            log(f"Search area selected.", "OK")
            
            screenshot2 = grab_full_screen()
            picker = ColorPicker(screenshot2)
            result = picker.run()
            
            hsv = result if result else DEFAULT_BOBBER_HSV
            BOBBER_COLOR_RANGES = hsv_to_ranges(*hsv)
            search_region = region
            
            data = {"region": list(region), "hsv": list(hsv)}
            CALIBRATION_FILE.write_text(json.dumps(data, indent=2))
            
            log(f"Calibration successful and saved!", "OK")
            
        threading.Thread(target=_calib, daemon=True).start()

    def update_bot(self):
        def _update():
            log("Checking for updates from GitHub...", "INFO")
            try:
                import urllib.request
                base_url = "https://raw.githubusercontent.com/toferraz-dev/Ferraz-Rotations/main/WowFishing/"
                files_to_check = [
                    "wow_fisher_gui.py", 
                    "FishGUI.bat", 
                    "requirements.txt", 
                    "README.md",
                    "wow_fisher.py",
                    "Fish.bat",
                    "Baixar_Python.url",
                    "icon.ico",
                    "icon.png"
                ]
                updated = False
                
                for file_name in files_to_check:
                    try:
                        url = base_url + file_name
                        req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
                        with urllib.request.urlopen(req, timeout=7) as response:
                            remote_data = response.read()
                            
                        local_path = Path(__file__).parent / file_name
                        is_binary = file_name.endswith(('.png', '.ico'))
                        
                        if is_binary:
                            if not local_path.exists() or local_path.read_bytes() != remote_data:
                                local_path.write_bytes(remote_data)
                                updated = True
                        else:
                            remote_text = remote_data.decode('utf-8').replace('\r\n', '\n')
                            if local_path.exists():
                                local_text = local_path.read_text(encoding='utf-8').replace('\r\n', '\n')
                                if local_text != remote_text:
                                    local_path.write_text(remote_text, encoding='utf-8')
                                    updated = True
                            else:
                                local_path.write_text(remote_text, encoding='utf-8')
                                updated = True
                    except Exception:
                        pass # Silently proceed if a single file has issues
                
                if updated:
                    log("Bot updated successfully! Please re-open the bot.", "OK")
                else:
                    log("Bot is already up to date!", "OK")
            except Exception as e:
                log(f"Failed to update automatically: {e}", "ERROR")
                
        threading.Thread(target=_update, daemon=True).start()

if __name__ == "__main__":
    # Ensure single instance
    mutex_name = "FerrazFishingWoW_Global_Instance_Lock"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if not mutex or ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        import tkinter.messagebox
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        tkinter.messagebox.showerror("Error", "The bot is already running! Please check your taskbar.")
        sys.exit(0)

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.04
    App().mainloop()

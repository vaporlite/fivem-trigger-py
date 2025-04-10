import customtkinter as ctk
import tkinter as tk
from PIL import ImageGrab
import os, time, ctypes, keyboard, threading, sys, requests
from typing import Tuple

# Set customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

PRIMARY_COLOR = "#4B70C9"
HOVER_COLOR = "#3A5DA0"
BG_COLOR = "#1A1A1A"

# Windows input functions
SendInput = ctypes.windll.user32.SendInput

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def is_color_match(color, target, tol):
    return all(abs(c - t) <= tol for c, t in zip(color, target))

class AtillaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.font_family = "Roboto"
        
        self.app_version = "1.0.0"  # Local version
        self.online_version_url = "https://raw.githubusercontent.com/vaporlite/atilla-key/refs/heads/main/key.txt"
        
        self.title(f"Atilla Private v{self.app_version}")
        self.geometry("700x500")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        
        # Bot variables
        self.screenMiddle = (960, 540)
        self.colorCode = (185, 76, 77)
        self.active = False
        self.tol = 20
        self.delay = 0
        self.check_interval = 0.05
        self.keybind = "g"
        self.toggle_mode = "toggle"
        self.running = True
        self.last_toggle_time = 0
        self.last_screen_capture = time.time()
        self.capture_rate_limit = 0.1
        self.current_tab = "settings"
        
        self.create_auth_ui()
        
    def create_auth_ui(self):
        self.clear_window()
        
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(expand=True)
        
        logo_label = ctk.CTkLabel(
            logo_frame, 
            text="Atilla Private", 
            font=ctk.CTkFont(family=self.font_family, size=36, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        logo_label.pack(pady=20)
        
        self.status_label = ctk.CTkLabel(
            logo_frame,
            text="Checking version...",
            font=ctk.CTkFont(family=self.font_family, size=14)
        )
        self.status_label.pack(pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(logo_frame)
        self.progress_bar.pack(pady=20, padx=100)
        self.progress_bar.set(0)
        
        self.after(500, self.perform_auth)
    
    def perform_auth(self):
        self.progress_bar.set(0.3)
        self.status_label.configure(text="Fetching online version...")
        
        try:
            response = requests.get(self.online_version_url, timeout=5)
            if response.status_code == 200:
                online_version = response.text.strip()
                self.progress_bar.set(0.6)
                self.status_label.configure(text="Verifying version...")
                self.after(1000, lambda: self.check_version(online_version))
            else:
                self.show_auth_error("Failed to fetch version")
        except requests.RequestException:
            self.show_auth_error("No internet connection")
    
    def check_version(self, online_version):
        self.progress_bar.set(0.8)
        if online_version == "2.0.0" and self.app_version != online_version:
            self.show_auth_error(f"Version mismatch!\nRequired: {online_version}\nCurrent: {self.app_version}")
        else:
            self.status_label.configure(text="Authentication successful!")
            self.progress_bar.set(1.0)
            self.after(1000, self.create_main_ui)
    
    def show_auth_error(self, message):
        self.status_label.configure(text="Authentication failed!")
        self.progress_bar.set(0)
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Authentication Error")
        error_dialog.geometry("300x200")
        error_dialog.resizable(False, False)
        error_dialog.configure(fg_color="#202020")
        error_dialog.transient(self)
        error_dialog.grab_set()
        
        ctk.CTkLabel(
            error_dialog,
            text=message,
            font=ctk.CTkFont(family=self.font_family, size=14),
            justify="center"
        ).pack(pady=20)
        ctk.CTkButton(
            error_dialog,
            text="Exit",
            command=lambda: [self.destroy(), sys.exit(0)],
            fg_color=PRIMARY_COLOR,
            hover_color=HOVER_COLOR,
            font=ctk.CTkFont(family=self.font_family, size=12)
        ).pack(pady=10)
    
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    def create_main_ui(self):
        self.clear_window()
        
        main_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Atilla Private",
            font=ctk.CTkFont(family=self.font_family, size=24, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        title_label.pack(side="left")
        
        version_label = ctk.CTkLabel(
            header_frame,
            text=f"v{self.app_version}",
            font=ctk.CTkFont(family=self.font_family, size=12),
            text_color=PRIMARY_COLOR
        )
        version_label.pack(side="left", padx=10)
        
        content_frame = ctk.CTkFrame(main_frame, fg_color="#202020")
        content_frame.pack(fill="both", expand=True)
        
        tab_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        tab_frame.pack(fill="x", pady=10)
        
        config_button = ctk.CTkButton(
            tab_frame,
            text="Settings",
            command=self.create_config_ui,
            fg_color=PRIMARY_COLOR,
            hover_color=HOVER_COLOR,
            font=ctk.CTkFont(family=self.font_family, size=14),
            width=100
        )
        config_button.pack(side="left", padx=5)
        
        activation_button = ctk.CTkButton(
            tab_frame,
            text="Activation",
            command=self.create_activation_ui,
            fg_color=PRIMARY_COLOR,
            hover_color=HOVER_COLOR,
            font=ctk.CTkFont(family=self.font_family, size=14),
            width=100
        )
        activation_button.pack(side="left", padx=5)
        
        exit_button = ctk.CTkButton(
            tab_frame,
            text="Exit",
            command=self.on_closing,
            fg_color=PRIMARY_COLOR,
            hover_color=HOVER_COLOR,
            font=ctk.CTkFont(family=self.font_family, size=14),
            width=100
        )
        exit_button.pack(side="right", padx=5)
        
        self.content_area = ctk.CTkFrame(content_frame, fg_color="#252525")
        self.content_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.create_config_ui()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_config_ui(self):
        self.current_tab = "settings"
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        scroll_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        header_label = ctk.CTkLabel(
            scroll_frame,
            text="Settings",
            font=ctk.CTkFont(family=self.font_family, size=18, weight="bold")
        )
        header_label.pack(pady=5)
        
        color_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        color_frame.pack(fill="x", pady=5)
        
        color_label = ctk.CTkLabel(color_frame, text="Target Color (RGB)", font=ctk.CTkFont(family=self.font_family, size=14))
        color_label.pack(anchor="w", pady=2)
        
        self.r_var = tk.IntVar(value=self.colorCode[0])
        self.g_var = tk.IntVar(value=self.colorCode[1])
        self.b_var = tk.IntVar(value=self.colorCode[2])
        
        for label, var in [("R:", self.r_var), ("G:", self.g_var), ("B:", self.b_var)]:
            frame = ctk.CTkFrame(color_frame, fg_color="transparent")
            frame.pack(fill="x", pady=2)
            ctk.CTkLabel(frame, text=label, width=20, font=ctk.CTkFont(family=self.font_family, size=12)).pack(side="left")
            ctk.CTkSlider(frame, from_=0, to=255, variable=var, progress_color=PRIMARY_COLOR).pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkEntry(frame, width=50, textvariable=var, font=ctk.CTkFont(family=self.font_family, size=12)).pack(side="left")
        
        settings = [
            ("Tolerance", tk.IntVar(value=self.tol), 0, 50),
            ("Check Interval (ms)", tk.DoubleVar(value=self.check_interval * 1000), 10, 100),
            ("Response Delay (ms)", tk.DoubleVar(value=self.delay * 1000), 0, 500)
        ]
        
        for name, var, min_val, max_val in settings:
            frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            ctk.CTkLabel(frame, text=name, font=ctk.CTkFont(family=self.font_family, size=14)).pack(anchor="w", pady=2)
            slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
            slider_frame.pack(fill="x")
            ctk.CTkSlider(slider_frame, from_=min_val, to=max_val, variable=var, progress_color=PRIMARY_COLOR).pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkEntry(slider_frame, width=50, textvariable=var, font=ctk.CTkFont(family=self.font_family, size=12)).pack(side="left")
        
        keybind_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        keybind_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(keybind_frame, text="Keybind", font=ctk.CTkFont(family=self.font_family, size=14)).pack(anchor="w", pady=2)
        
        self.keybind_var = tk.StringVar(value=self.keybind)
        keybind_label = ctk.CTkLabel(keybind_frame, textvariable=self.keybind_var, font=ctk.CTkFont(family=self.font_family, size=12), width=100)
        keybind_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            keybind_frame,
            text="Set Keybind",
            command=self.set_keybind,
            fg_color=PRIMARY_COLOR,
            hover_color=HOVER_COLOR,
            font=ctk.CTkFont(family=self.font_family, size=12),
            width=100
        ).pack(side="left")
        
        mode_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        mode_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(mode_frame, text="Trigger Mode", font=ctk.CTkFont(family=self.font_family, size=14)).pack(anchor="w", pady=2)
        
        self.mode_var = tk.StringVar(value=self.toggle_mode)
        ctk.CTkOptionMenu(
            mode_frame,
            values=["toggle", "hold"],
            variable=self.mode_var,
            font=ctk.CTkFont(family=self.font_family, size=12),
            fg_color=PRIMARY_COLOR,
            button_color=PRIMARY_COLOR,
            button_hover_color=HOVER_COLOR
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            scroll_frame,
            text="Save",
            command=lambda: self.save_config(
                self.r_var.get(), self.g_var.get(), self.b_var.get(),
                settings[0][1].get(), settings[1][1].get(), settings[2][1].get()
            ),
            fg_color=PRIMARY_COLOR,
            hover_color=HOVER_COLOR,
            font=ctk.CTkFont(family=self.font_family, size=14)
        ).pack(pady=10)
    
    def set_keybind(self):
        keyboard.unhook_all()
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Set Keybind")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color="#202020")
        
        ctk.CTkLabel(
            dialog,
            text="waiting for key press...",
            font=ctk.CTkFont(family=self.font_family, size=14)
        ).pack(pady=20)
        
        def on_key_press(event):
            key = event.name
            if key in ['left', 'right', 'middle', 'xbutton1', 'xbutton2'] or len(key) == 1:
                self.keybind = key
                self.keybind_var.set(key)
                self.register_keybind()
                dialog.destroy()
        
        keyboard.hook(on_key_press)
        dialog.protocol("WM_DELETE_WINDOW", lambda: [keyboard.unhook_all(), dialog.destroy()])
    
    def register_keybind(self):
        keyboard.unhook_all()
        if self.toggle_mode == "toggle":
            keyboard.on_press_key(self.keybind, self.keyboard_handler_toggle)
        else:
            keyboard.on_press_key(self.keybind, self.keyboard_handler_hold_press)
            keyboard.on_release_key(self.keybind, self.keyboard_handler_hold_release)
    
    def save_config(self, r, g, b, tol, interval, delay):
        self.colorCode = (r, g, b)
        self.tol = tol
        self.check_interval = max(0.01, interval / 1000)
        self.delay = delay / 1000
        self.toggle_mode = self.mode_var.get()
        
        self.register_keybind()
        
        save_dialog = ctk.CTkToplevel(self)
        save_dialog.title("Saved")
        save_dialog.geometry("200x100")
        save_dialog.resizable(False, False)
        save_dialog.configure(fg_color="#202020")
        
        ctk.CTkLabel(
            save_dialog,
            text="Settings Saved!",
            font=ctk.CTkFont(family=self.font_family, size=14)
        ).pack(pady=20)
        ctk.CTkButton(
            save_dialog,
            text="OK",
            command=save_dialog.destroy,
            fg_color=PRIMARY_COLOR,
            hover_color=HOVER_COLOR,
            font=ctk.CTkFont(family=self.font_family, size=12)
        ).pack(pady=10)
    
    def create_activation_ui(self):
        self.current_tab = "activation"
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        status_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        status_frame.pack(expand=True)
        
        header_label = ctk.CTkLabel(
            status_frame,
            text="Activation",
            font=ctk.CTkFont(family=self.font_family, size=18, weight="bold")
        )
        header_label.pack(pady=5)
        
        inner_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        inner_frame.pack(pady=20)
        
        ctk.CTkLabel(
            inner_frame,
            text="Status:",
            font=ctk.CTkFont(family=self.font_family, size=14)
        ).pack(pady=5)
        
        self.status_indicator = ctk.CTkLabel(
            inner_frame,
            text="Inactive",
            font=ctk.CTkFont(family=self.font_family, size=20, weight="bold"),
            text_color="gray"
        )
        self.status_indicator.pack()
        
        self.status_light = ctk.CTkFrame(inner_frame, width=30, height=30, fg_color="gray", corner_radius=15)
        self.status_light.pack(pady=10)
        
        self.toggle_button = ctk.CTkButton(
            inner_frame,
            text="Start Bot",
            command=self.toggle_bot,
            fg_color=PRIMARY_COLOR,
            hover_color=HOVER_COLOR,
            font=ctk.CTkFont(family=self.font_family, size=14),
            width=120
        )
        self.toggle_button.pack(pady=10)
    
    def toggle_bot(self):
        self.active = not self.active
        if self.active:
            self.status_indicator.configure(text="Active", text_color="green")
            self.status_light.configure(fg_color="green")
            self.toggle_button.configure(text="Stop Bot")
        else:
            self.status_indicator.configure(text="Inactive", text_color="gray")
            self.status_light.configure(fg_color="gray")
            self.toggle_button.configure(text="Start Bot")
        if not hasattr(self, 'bot_thread') or not self.bot_thread.is_alive():
            self.bot_thread = threading.Thread(target=self.bot_loop, daemon=True)
            self.bot_thread.start()
    
    def bot_loop(self):
        while self.running:
            if self.active:
                current_time = time.time()
                if current_time - self.last_screen_capture >= self.capture_rate_limit:
                    self.last_screen_capture = current_time
                    img = ImageGrab.grab(bbox=(self.screenMiddle[0]-1, self.screenMiddle[1]-1, self.screenMiddle[0]+1, self.screenMiddle[1]+1))
                    color = img.getpixel((1, 1))
                    
                    if is_color_match(color, self.colorCode, self.tol):
                        time.sleep(self.delay)
                        PressKey(0x34)
                        time.sleep(0.01)
                        ReleaseKey(0x34)
            time.sleep(self.check_interval)
    
    def keyboard_handler_toggle(self, e):
        if self.current_tab == "activation":
            current_time = time.time()
            if current_time - self.last_toggle_time > 0.2:
                self.last_toggle_time = current_time
                self.toggle_bot()
    
    def keyboard_handler_hold_press(self, e):
        if self.current_tab == "activation":
            self.active = True
            self.status_indicator.configure(text="Active", text_color="green")
            self.status_light.configure(fg_color="green")
            self.toggle_button.configure(text="Stop Bot")
            if not hasattr(self, 'bot_thread') or not self.bot_thread.is_alive():
                self.bot_thread = threading.Thread(target=self.bot_loop, daemon=True)
                self.bot_thread.start()
    
    def keyboard_handler_hold_release(self, e):
        if self.current_tab == "activation":
            self.active = False
            self.status_indicator.configure(text="Inactive", text_color="gray")
            self.status_light.configure(fg_color="gray")
            self.toggle_button.configure(text="Start Bot")
    
    def on_closing(self):
        self.running = False
        keyboard.unhook_all()
        self.destroy()

if __name__ == "__main__":
    app = AtillaApp()
    app.register_keybind()
    app.mainloop()

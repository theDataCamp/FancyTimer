import tkinter as tk
from tkinter import ttk
import pyautogui
import datetime
import threading


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer App")

        self.timer = Timer(self.on_timer_done)

        self.screenshot_var = tk.BooleanVar(value=False)
        self.setup_gui()

    def setup_gui(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=20)

        self.hour_var = tk.StringVar(value="0")
        self.min_var = tk.StringVar(value="0")
        self.sec_var = tk.StringVar(value="0")

        row_num = 0

        # Spinbox for Hours
        hour_spinbox = ttk.Spinbox(frame, from_=0, to=23, textvariable=self.hour_var, width=5)
        hour_spinbox.grid(row=row_num, column=0)
        ttk.Label(frame, text="Hours").grid(row=row_num + 1, column=0)

        # Spinbox for Minutes
        min_spinbox = ttk.Spinbox(frame, from_=0, to=59, textvariable=self.min_var, width=5)
        min_spinbox.grid(row=row_num, column=1)
        ttk.Label(frame, text="Minutes").grid(row=row_num + 1, column=1)

        # Spinbox for Seconds
        sec_spinbox = ttk.Spinbox(frame, from_=0, to=59, textvariable=self.sec_var, width=5)
        sec_spinbox.grid(row=row_num, column=2)
        ttk.Label(frame, text="Seconds").grid(row=row_num + 1, column=2)

        self.start_button = ttk.Button(frame, text="Start", command=self.on_start)
        self.start_button.grid(row=row_num + 2, column=0, pady=20)

        self.stop_button = ttk.Button(frame, text="Stop", command=self.on_stop, state=tk.DISABLED)
        self.stop_button.grid(row=row_num + 2, column=1, pady=20)

        # Add a Pause/Unpause button
        self.pause_button = ttk.Button(frame, text="Pause/Unpause", command=self.on_pause, state=tk.DISABLED)
        self.pause_button.grid(row=row_num + 2, column=2, pady=20)

        # Checkbutton for screenshot option
        self.screenshot_check = ttk.Checkbutton(frame, text="Take Screenshot", variable=self.screenshot_var)
        self.screenshot_check.grid(row=row_num + 3, column=0, pady=10, columnspan=2)

        self.time_display = ttk.Label(self.root, text="00:00:00", font=("Arial", 30))
        self.time_display.pack(pady=20)

    def on_start(self):
        h = int(self.hour_var.get())
        m = int(self.min_var.get())
        s = int(self.sec_var.get())

        if self.timer.paused:
            self.timer.resume(self.update_display)
        else:
            self.start_button['state'] = tk.DISABLED
            self.pause_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.NORMAL
            thread = threading.Thread(target=self.timer.start, args=(h, m, s, self.update_display))
            thread.start()

    def on_pause(self):
        self.timer.pause(self.update_display)
        if self.timer.paused:
            self.start_button['state'] = tk.DISABLED
            self.stop_button['state'] = tk.NORMAL
        else:
            self.start_button['state'] = tk.DISABLED
            self.stop_button['state'] = tk.NORMAL

    def on_stop(self):
        self.timer.stop()
        # Reset spinboxes to user-set values
        self.hour_var.set(self.hour_var.get())
        self.min_var.set(self.min_var.get())
        self.sec_var.set(self.sec_var.get())
        self.update_display("00:00:00")
        self.start_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED
        self.pause_button['state'] = tk.DISABLED

    def update_display(self, time_str):
        self.time_display.config(text=time_str)

    def on_timer_done(self):
        if self.screenshot_var.get():
            now = datetime.datetime.now()
            filename = now.strftime("%Y_%m_%d__%H_%M_%S.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)

        FlashWindow(self.root)

        self.start_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED
        self.pause_button['state'] = tk.DISABLED


class FlashWindow:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.geometry("600x300")
        now = datetime.datetime.now()
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        self.window.title(formatted_datetime)
        self.current_color = "red"
        self.window.config(bg=self.current_color)
        self.change_color()

    def change_color(self):
        if self.current_color == "red":
            self.window.config(bg="yellow")
            self.current_color = "yellow"
        else:
            self.window.config(bg="red")
            self.current_color = "red"
        self.window.after(500, self.change_color)


class Timer:
    def __init__(self, callback):
        self.callback = callback
        self.stop_flag = False
        self.paused = False
        self.remaining = 0

    def start(self, hours, mins, secs, update_callback):
        self.total_seconds = hours * 3600 + mins * 60 + secs
        self.stop_flag = False
        self.paused = False
        self.countdown(self.total_seconds, update_callback)

    def countdown(self, time_left, update_callback):
        if self.stop_flag or self.paused:
            return

        self.remaining = time_left
        mins, sec = divmod(time_left, 60)
        hours, mins = divmod(mins, 60)
        time_str = f"{hours:02}:{mins:02}:{sec:02}"
        update_callback(time_str)

        if time_left == 0:
            self.callback()
        else:
            self.root_after_id = root.after(1000, self.countdown, time_left - 1, update_callback)

    def pause(self, update_callback=None):
        if not self.paused:
            self.paused = True
        else:
            self.paused = False
            self.resume(update_callback)

    def resume(self, update_callback):
        self.stop_flag = False
        self.paused = False
        self.countdown(self.remaining, update_callback)

    def stop(self):
        self.stop_flag = True
        self.remaining = 0
        self.paused = False
        try:
            root.after_cancel(self.root_after_id)
        except AttributeError:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()

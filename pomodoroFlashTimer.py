import tkinter as tk
from tkinter import simpledialog
import time
import multiprocessing
import argparse
import sys

def flash_screen(color, steps, interval):
    """Flash the screen with the specified color."""
    print(f"Starting screen flash: {color}...")
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(bg=color, highlightthickness=0)
    root.attributes("-alpha", 0.0)
    
    # Flash effect
    if color == "red":
        # Toggle alpha for red flash
        alpha = 0.0
        for _ in range(steps):
            alpha = 0.15 if alpha == 0.5 else 0.5
            root.attributes("-alpha", alpha)
            root.update()
            time.sleep(interval / 1000)
    else:
        # Gradual alpha increase for green flash
        alpha = 0.0
        step_size = 0.6 / steps
        for _ in range(steps):
            alpha += step_size
            root.attributes("-alpha", alpha)
            root.update()
            time.sleep(interval / 1000)
    
    print("Flashing complete, closing window...")
    root.destroy()
    print(f"{color} flash completed.")

def background_task(duration, color, stop_event):
    """Background task that waits for the specified duration and then flashes the screen."""
    duration_seconds = duration * 60
    print(f"Background task started: {duration} minutes ({color} flash)")
    
    # Wait for the time to elapse or for stop_event to be set
    start_time = time.time()
    while time.time() - start_time < duration_seconds and not stop_event.is_set():
        time.sleep(1)  # Check frequently for stop_event
    
    # Flash the screen if not interrupted
    if not stop_event.is_set():
        print(f"Flashing screen {color}...")
        flash_screen(color, 5, 500)
        
    print(f"{color.capitalize()} timer completed!")

class TimerApp(tk.Tk):
    def __init__(self, time_limit, bg_color):
        super().__init__()
        self.time_limit = time_limit * 60
        self.bg_color = bg_color

        # Configure window
        self.title("Timer App")
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.geometry("81x50+0-50")  # Size and position (bottom left)
        self.configure(bg="", highlightthickness=0)
        self.attributes("-alpha", 0.5)

        # Create timer display
        self.timer_label = tk.Label(self, font=("Arial", 24), text="00:00", 
                                   fg="black", bg=self.bg_color)
        self.timer_label.pack(expand=True, fill=tk.BOTH)

        # Start the timer
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        """Update the timer display."""
        elapsed_time = time.time() - self.start_time
        left_time = self.time_limit - elapsed_time

        if left_time <= 0.0:
            self.after(500, self.destroy)
            return
        
        minutes, seconds = divmod(int(left_time), 60)
        timer_text = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.config(text=timer_text)

        # Schedule next update (slightly less than 5 seconds)
        self.after(4970, self.update_timer)

def run_timer_session(duration, color, session_name):
    """Run a complete timer session with background flash process."""
    print(f"Starting {session_name} session: {duration} minutes")
    
    # Create and start background process
    stop_event = multiprocessing.Event()
    bg_process = multiprocessing.Process(
        target=background_task, 
        args=(duration, color, stop_event)
    )
    bg_process.daemon = True
    bg_process.start()
    
    # Create and run timer window
    timer = TimerApp(duration, "white" if color == "red" else "green")
    timer.mainloop()
    
    # Clean up
    print(f"{session_name} timer finished, stopping background process...")
    stop_event.set()
    bg_process.join(timeout=2)
    
    return stop_event, bg_process

def center_dialog(root_window):
    """Ensure the root window is positioned for centered dialogs."""
    # Get screen dimensions
    screen_width = root_window.winfo_screenwidth()
    screen_height = root_window.winfo_screenheight()
    
    # Set position to center of screen
    x = (screen_width - 1) // 2
    y = (screen_height - 1) // 2
    root_window.geometry(f"+{x}+{y}")

def get_user_input(title, prompt, default_value, min_value, max_value):
    """Show dialog and get user input with positioning."""
    root = tk.Tk()
    root.withdraw()
    
    # Ensure the dialog will be centered
    center_dialog(root)
    
    # Use standard simpledialog but with proper positioning
    value = simpledialog.askinteger(
        title, prompt, 
        initialvalue=default_value,
        minvalue=min_value, 
        maxvalue=max_value,
        parent=root
    )
    
    root.destroy()
    return value

if __name__ == "__main__":
    try:
        print("Starting Pomodoro Timer application...")
        multiprocessing.freeze_support()

        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Pomodoro Timer")
        parser.add_argument("--worktime", type=int, help="Work time in minutes")
        parser.add_argument("--breaktime", type=int, help="Break time in minutes")
        args = parser.parse_args()

        # Default values
        default_work_time = 25
        default_break_time = 5

        # Get work time
        if args.worktime is None:
            print("Displaying work time dialog...")
            work_time = get_user_input(
                "Work Time",
                "Enter work time in minutes:",
                default_work_time,
                1,
                120
            )
            
            if work_time is None:
                print("No work time provided. Exiting...")
                sys.exit(0)
        else:
            work_time = args.worktime

        # Get break time
        if args.breaktime is None:
            print("Displaying break time dialog...")
            break_time = get_user_input(
                "Break Time",
                "Enter break time in minutes:",
                default_break_time,
                1,
                30
            )
            
            if break_time is None:
                print("No break time provided. Using default...")
                break_time = default_break_time
        else:
            break_time = args.breaktime

        print(f"Starting Pomodoro with work time: {work_time} min, break time: {break_time} min")

        # Run work session
        work_stop_event, work_process = run_timer_session(work_time, "red", "Work")
        time.sleep(0.5)  # Small pause between sessions
        
        # Run break session
        break_stop_event, break_process = run_timer_session(break_time, "green", "Break")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

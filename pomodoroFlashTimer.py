import tkinter as tk
from tkinter import simpledialog
import time
import multiprocessing
import argparse

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
        for _ in range(steps):
            alpha = 0.15 if root.attributes("-alpha") == 0.5 else 0.5
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

if __name__ == "__main__":
    multiprocessing.freeze_support()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Pomodoro Timer")
    parser.add_argument("--worktime", type=int, help="Work time in minutes")
    parser.add_argument("--breaktime", type=int, help="Break time in minutes")
    args = parser.parse_args()

    # Default break time in minutes
    default_break_time = 5

    # Create a single root window for dialogs
    root = tk.Tk()
    root.withdraw()

    # Get work time from command line or dialog
    if args.worktime is None:
        work_time = simpledialog.askinteger("Work Time", "Enter work time in minutes:", 
                                           minvalue=1, maxvalue=120, initialvalue=25)
        if work_time is None:
            print("No work time provided. Exiting...")
            root.destroy()
            exit()
    else:
        work_time = args.worktime

    # Get break time from command line or dialog
    if args.breaktime is None:
        break_time = simpledialog.askinteger("Break Time", "Enter break time in minutes:", 
                                            minvalue=1, maxvalue=30, initialvalue=default_break_time)
        if break_time is None:
            print("No break time provided. Using default...")
            break_time = default_break_time
    else:
        break_time = args.breaktime

    # Clean up the root window
    root.destroy()

    try:
        # Run work session
        work_stop_event, work_process = run_timer_session(work_time, "red", "Work")
        time.sleep(0.5)  # Small pause between sessions
        
        # Run break session
        break_stop_event, break_process = run_timer_session(break_time, "green", "Break")
        
    except KeyboardInterrupt:
        print("Exiting due to keyboard interrupt...")
        # Clean up any active processes
        for event, process in [(work_stop_event, work_process) 
                              if 'work_stop_event' in locals() else (None, None),
                              (break_stop_event, break_process)
                              if 'break_stop_event' in locals() else (None, None)]:
            if event:
                event.set()
            if process and process.is_alive():
                process.terminate()

import tkinter as tk
from tkinter import simpledialog
import time
import multiprocessing
import argparse

# Function to flash the screen
def flash_screenRed(steps, interval):
    print("Starting flash_screenRed...")
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)  # Ensure that the window stays on top
    root.configure(bg="red", highlightthickness=0)  # Set the background to transparent
    root.attributes("-alpha", 0.0)  # Set the transparency level (0.0 - 1.0)
    alpha = 0.0
    # step_size = (0.6 - 0.0) / steps
    for _ in range(steps):
        alpha = 0.15 if alpha == 0.5 else 0.5
        root.attributes("-alpha", alpha)
        root.update()
        time.sleep(interval / 1000)
    print("Flashing complete, destroying root...")
    root.destroy()  # Direct destroy instead of using after()
    print("flash_screenRed completed.")

# Function for the background task
def background_task1(WorkTime, stop_event):
    # Set the time interval after which the screen will flash (in seconds)
    flash_interval = WorkTime * 60
    print(f"Background task for work started with interval: {flash_interval} seconds")

    # Wait for the time to elapse or for stop_event to be set
    start_time = time.time()
    while time.time() - start_time < flash_interval and not stop_event.is_set():
        time.sleep(1)  # Check more frequently for stop_event
    
    # If stop_event hasn't been set yet, flash the screen
    if not stop_event.is_set():
        print("Flashing screen red...")
        flash_screenRed(5, 500)
        
    print("Work Time is over!")

# Function to flash the screen
def flash_screenGreen(steps, interval):
    print("Starting flash_screenGreen...")
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)  # Ensure that the window stays on top
    root.configure(bg="green", highlightthickness=0)  # Set the background to transparent
    root.attributes("-alpha", 0.1)  # Set the transparency level (0.0 - 1.0)
    alpha = 0.0
    step_size = (0.6 - 0.0) / steps
    for _ in range(steps):
        alpha += step_size
        root.attributes("-alpha", alpha)
        root.update()
        time.sleep(interval / 1000)  # Convert milliseconds to seconds
    print("Flashing complete, destroying root...")
    root.destroy()  # Direct destroy
    print("flash_screenGreen completed.")

# Function for the background task
def background_task2(BreakTime, stop_event):
    flash_interval = BreakTime * 60
    print(f"Background task for break started with interval: {flash_interval} seconds")

    # Wait for the time to elapse or for stop_event to be set
    start_time = time.time()
    while time.time() - start_time < flash_interval and not stop_event.is_set():
        time.sleep(1)  # Check more frequently for stop_event
    
    # If stop_event hasn't been set yet, flash the screen
    if not stop_event.is_set():
        print("Flashing screen green...")
        flash_screenGreen(5, 500)
        
    print("Break Time is over!")


class TimerApp(tk.Tk):
    def __init__(self, timeLimit, bgColor):
        super().__init__()

        self.timeLimit = timeLimit * 60
        self.bgColor = bgColor

        self.title("Timer App")
        self.attributes("-topmost", True)  # Ensure the window stays on top
        self.overrideredirect(True)  # Remove the window decorations (title bar, border)
        self.geometry("81x50")  # Set the window size
        self.geometry("+0-50")   # Position the window at the bottom left corner
        self.configure(bg="", highlightthickness=0)  # Set the background to transparent
        self.attributes("-alpha", 0.5)  # Set the transparency level (0.0 - 1.0)

        # Create a label to display the timer
        self.timer_label = tk.Label(self, font=("Arial", 24), text="00:00", fg="black", bg=self.bgColor)
        self.timer_label.pack(expand=True, fill=tk.BOTH)

        # Start the timer
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        elapsed_time = time.time() - self.start_time
        left_time = self.timeLimit - elapsed_time

        if left_time <= 0.0:
            self.after(500, self.destroy)
            return
        
        minutes, seconds = divmod(int(left_time), 60)
        timer_text = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.config(text=timer_text)

        # Schedule the next update after 5 seconds - not exactly 5 seconds to avoid non multiples of 5 in seconds.
        self.after(4970, self.update_timer)


if __name__ == "__main__":
    multiprocessing.freeze_support()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Pomodoro Timer")
    parser.add_argument("--worktime", type=int, help="Work time in minutes")
    args = parser.parse_args()

    # If no command-line argument is provided, show a dialog box
    if args.worktime is None:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        WorkTime = simpledialog.askinteger("Input", "Enter work time in minutes:", minvalue=1, maxvalue=120)
        root.destroy()  # Make sure to destroy the root window
        if WorkTime is None:
            print("No input provided. Exiting...")
            exit()
    else:
        WorkTime = args.worktime

    BreakTime = 1

    try:
        print("Main application code is running...")
        
        # Create work timer objects
        stop_event1 = multiprocessing.Event()
        background_process1 = multiprocessing.Process(target=background_task1, args=(WorkTime, stop_event1))
        background_process1.daemon = True
        
        # Start work session
        print("Starting background process for work timer...")
        background_process1.start()
        print("Work timer started...")
        timerWork = TimerApp(WorkTime, "white")
        timerWork.mainloop()
        
        # Clean up work session
        print("Work timer finished, signaling background process to stop...")
        stop_event1.set()
        background_process1.join(timeout=2)  # Add timeout to prevent hanging
        print("Background process for work has finished.")
        
        # Small delay between sessions
        time.sleep(0.5)
        
        # Create break timer objects
        stop_event2 = multiprocessing.Event()
        background_process2 = multiprocessing.Process(target=background_task2, args=(BreakTime, stop_event2))
        background_process2.daemon = True
        
        # Start break session
        print("Starting background process for break...")
        background_process2.start()
        print("Break timer started...")
        timerBreak = TimerApp(BreakTime, "green")
        timerBreak.mainloop()
        
        # Clean up break session
        print("Break timer finished, signaling background process to stop...")
        stop_event2.set()
        background_process2.join(timeout=2)  # Add timeout to prevent hanging
        print("Background process for break has finished.")

    except KeyboardInterrupt:
        print("Exiting...")
        stop_event1.set() if 'stop_event1' in locals() else None
        stop_event2.set() if 'stop_event2' in locals() else None
        if 'background_process1' in locals() and background_process1.is_alive():
            background_process1.terminate()
        if 'background_process2' in locals() and background_process2.is_alive():
            background_process2.terminate()

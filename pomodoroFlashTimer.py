import tkinter as tk
from tkinter import simpledialog
import time
import multiprocessing
import argparse

# Function to flash the screen
def flash_screenRed(steps, interval):
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)  # Ensure that the window stays on top
    root.configure(bg="red", highlightthickness=0)  # Set the background to transparent
    root.attributes("-alpha", 0.0)  # Set the transparency level (0.0 - 1.0)
    alpha = 0.0
    # step_size = (0.6 - 0.0) / steps
    for _ in range(steps):
        alpha = 0.15 if alpha == 0.5 else 0.5  # Toggle between two alpha values
        root.attributes("-alpha", alpha)
        root.update()
        time.sleep(interval / 1000)  # Convert milliseconds to seconds
    root.after(interval, root.destroy)  # Close the window after 1 second
    root.mainloop()

# Function for the background task
def background_task1(WorkTime):
    # Set the time interval after which the screen will flash (in seconds)
    flash_interval = WorkTime * 60

    while True:
        time.sleep(flash_interval)
        flash_screenRed(5, 500)
        break
    print ("Work Time is over!")

# Function to flash the screen
def flash_screenGreen(steps, interval):
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
    root.after(interval, root.destroy)  # Close the window after 1 second
    root.mainloop()

# Function for the background task
def background_task2(BreakTime):
    # Set the time interval after which the screen will flash (in seconds)
    flash_interval = BreakTime * 60

    while True:
        time.sleep(flash_interval)
        flash_screenGreen(5, 500)
        break


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
        if WorkTime is None:
            print("No input provided. Exiting...")
            exit()
    else:
        WorkTime = args.worktime

    BreakTime = 5

    # Create a new process for the background task
    background_process1 = multiprocessing.Process(target=background_task1, args=(WorkTime,))

    # Set the daemon property to True so that the background process terminates when the main process terminates
    background_process1.daemon = True

    # Create a new process for the background task
    background_process2 = multiprocessing.Process(target=background_task2, args=(BreakTime,))
    background_process2.daemon = True

    

    try:
        print("Main application code is running...")
        # Start the background process
        timerWork = TimerApp(WorkTime, "white")
        background_process1.start()
        print("Work timer started...")
        timerWork.mainloop()
        background_process1.join()

        timerBreak = TimerApp(BreakTime, "green")
        background_process2.start()
        print("Break timer started...")
        timerBreak.mainloop()
        background_process2.join()

    except KeyboardInterrupt:
        print("Exiting...")

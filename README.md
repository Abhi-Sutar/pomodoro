# Pomodoro Flash Timer

A Pomodoro timer application that uses screen flashes to indicate when work and break periods are complete.

## Description

Pomodoro Flash Timer is a simple desktop application that implements the Pomodoro Technique, a time management method that uses alternating work and break intervals. This implementation features:

- Customizable work time periods
- Configurable break periods (default: 5 minutes)
- Visual screen flash notifications at the end of each period
- Small, unobtrusive timer display in the corner of your screen
- Command-line or GUI input options

The timer displays in the bottom-left corner of your screen with a small, semi-transparent window that shows the remaining time. When a period ends, your screen will flash (red for work periods, green for break periods) to notify you.

## Features

- **Work Timer**: Configurable work period with a visual countdown
- **Break Timer**: Automatic transition to break time after work completes
- **Visual Notifications**: Full-screen flashes when timers complete
- **User-friendly Input**: Dialog boxes for configuring timer periods

## Installation

### Requirements

- Python 3.6+
- Required packages: tkinter, multiprocessing

### Setting Up

1. Clone this repository or download the source code
2. Ensure Python 3.6+ is installed on your system
3. No external packages are required as the app uses standard library modules

## Usage

### Running as a Python Script

```bash
# Basic usage (will prompt for work time)
python pomodoroFlashTimer.py

# Specify work time at launch (e.g., 25 minutes)
python pomodoroFlashTimer.py --worktime 25
```

### Using the Application

1. When started, the application will prompt you for a work time (in minutes)
2. A small timer window will appear in the bottom-left corner of your screen
3. When the work timer completes, the screen will flash red
4. A break timer will automatically start
5. When the break timer completes, the screen will flash green

## Creating an Executable

### Using PyInstaller

PyInstaller can package the application into a standalone executable:

1. Install PyInstaller if you don't have it already:
   ```bash
   pip install pyinstaller
   ```

2. Navigate to the project directory:
   ```bash
   cd path\to\pomodoro\folder
   ```

3. Create the executable with PyInstaller:
   ```bash
   # Basic single-file build
   pyinstaller --onefile pomodoroFlashTimer.py
   
   # For better performance (recommended)
   pyinstaller --onedir pomodoroFlashTimer.py
   
   # If you want an icon
   pyinstaller --onefile --icon=path\to\icon.ico pomodoroFlashTimer.py
   ```

4. The executable will be created in the `dist` folder
5. Run the executable directly or create a shortcut to it

### Using Dialogs with the Executable

When running the executable version:
- If you double-click the executable, it will show a dialog asking for work time
- You can also run it from the command line with the `--worktime` argument

## Troubleshooting

- **Screen Flashing Issues**: If screen flashing doesn't work, check if your system allows applications to create full-screen windows
- **Timer Not Visible**: The timer is designed to be unobtrusive. Look for a small window in the bottom-left corner of your screen
- **Process Not Ending**: If you need to force-quit, use Task Manager to end the process

## License

This project is available for personal use.

## Acknowledgments

- The Pomodoro Technique was developed by Francesco Cirillo
- Built with Python using tkinter for the interface
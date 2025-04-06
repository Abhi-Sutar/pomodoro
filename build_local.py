import subprocess
import sys
import os

# --- Config ---
entry_script = "pomodoroFlashTimer.py"
icon_path = "resources/pomodoro.ico"  # Make sure this is a valid .ico file
exe_name = "pomodoroFlashTimer.exe"
build_dir = "dist"

# --- Helpers ---
def run(cmd, check=True):
    print(f"\n🔧 Running: {cmd}")
    subprocess.run(cmd, check=check, shell=True)

# --- Version Info ---
print("🐍 Python version:")
run("python --version")

print("\n📦 Pip version:")
run("pip --version")

# --- Generate requirements.txt (ignoring this build script) ---
print("\n📋 Generating minimal requirements.txt with pipreqs (ignoring build_local.py)...")
# run("pip install pipreqs")
run(f"pipreqs . --force --ignore build_local.py")

# --- Install project dependencies ---
# print("\n📥 Installing dependencies...")
# run("pip install -r requirements.txt")

# --- Build executable ---
print("\n🔨 Building with PyInstaller...")
if not os.path.exists(icon_path):
    print(f"⚠️ Warning: Icon file not found at {icon_path}. Continuing without icon.")
    icon_arg = ""
else:
    icon_arg = f"--icon={icon_path}"

# Clear old build
if os.path.exists(build_dir):
    import shutil
    shutil.rmtree(build_dir)

# Run PyInstaller
run(f"pyinstaller --onefile --noconsole {icon_arg} --name {exe_name} {entry_script}")

print(f"\n✅ Build complete! Find your executable in the '{build_dir}' folder.")

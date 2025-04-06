import subprocess
import os
import glob

# --- Config ---
entry_script = "pomodoroFlashTimer.py"
icon_path = "resources/pomodoro.ico"  # Make sure this is a valid .ico file
exe_name = "pomodoroFlashTimer.exe"
build_dir = "dist"
run_pylint = True  # Set to False to skip Pylint checks

# --- Helpers ---
def run(cmd, check=True):
    print(f"\n🔧 Running: {cmd}")
    result = subprocess.run(cmd, check=check, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result

def check_and_install_package(package_name):
    """Check if a package is installed and install it if not."""
    try:
        __import__(package_name)
        print(f"✅ {package_name} is already installed")
    except ImportError:
        print(f"⚠️ {package_name} not found. Installing...")
        run(f"pip install {package_name}")

# --- Version Info ---
print("🐍 Python version:")
run("python --version")

print("\n📦 Pip version:")
run("pip --version")

# --- Generate requirements.txt (ignoring this build script) ---
print("\n📋 Generating minimal requirements.txt with pipreqs (ignoring build_local.py)...")
check_and_install_package("pipreqs")
run(f"pipreqs . --force --ignore build_local.py")

# --- Run Pylint (similar to GitHub Actions) ---
if run_pylint:
    print("\n🔍 Running Pylint checks...")
    check_and_install_package("pylint")
    
    # Check if .pylintrc exists, create it if not
    if not os.path.exists(".pylintrc"):
        print("⚠️ No .pylintrc found. Creating with recommended settings...")
        
        pylintrc_content = """[MASTER]
recursive=yes
ignore-patterns=.git,__pycache__,dist,build

[MESSAGES CONTROL]
disable=
    C0111,
    R0903,
    C0103,
    W0212,
    R0914,
    W0702,
    E1101

[FORMAT]
max-line-length=100
indent-string='    '

[REPORTS]
output-format=colorized
reports=yes

[BASIC]
good-names=i,j,k,ex,_,tk,id,ip,up,x,y

[DESIGN]
max-args=8
max-attributes=15
min-public-methods=1
max-public-methods=30

[SIMILARITIES]
min-similarity-lines=5
ignore-imports=yes
"""
        with open(".pylintrc", "w") as f:
            f.write(pylintrc_content)
    
    # Get all Python files
    python_files = glob.glob("**/*.py", recursive=True)
    python_files = [f for f in python_files if not f.startswith(("dist/", "build/"))]
    
    if python_files:
        print(f"Found {len(python_files)} Python files to check")
        pylint_command = f"pylint {' '.join(python_files)}"
        
        # Run Pylint but don't fail the build if it returns non-zero
        result = run(pylint_command, check=False)
        
        if result.returncode != 0:
            print("\n⚠️ Pylint found issues. See output above for details.")
            print("   The build will continue, but these issues would fail in CI/CD.")
        else:
            print("\n✅ Pylint checks passed!")
    else:
        print("No Python files found to check")

# --- Build executable ---
print("\n🔨 Building with PyInstaller...")
check_and_install_package("pyinstaller")

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

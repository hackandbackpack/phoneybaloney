"""Cross-platform installer for PhoneyBaloney."""
import os
import platform
import subprocess
import sys
from pathlib import Path


def run(cmd, check=True):
    """Run a command and return the result."""
    print(f"  Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  Error: {result.stderr.strip()}")
        return False
    return True


def detect_os():
    """Detect the operating system."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "mac"
    else:
        return "linux"


def check_python_version():
    """Ensure Python 3.10+."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 10):
        print(f"Error: Python 3.10+ required. You have {major}.{minor}")
        sys.exit(1)
    print(f"  Python {major}.{minor} detected")


def create_venv():
    """Create virtual environment."""
    if Path("venv").exists():
        print("  Virtual environment already exists")
        return
    print("  Creating virtual environment...")
    run(f"{sys.executable} -m venv venv")


def get_pip():
    """Get the pip command for the venv."""
    os_type = detect_os()
    if os_type == "windows":
        return str(Path("venv/Scripts/pip"))
    return str(Path("venv/bin/pip"))


def install_base():
    """Install base + LLM dependencies."""
    pip = get_pip()
    print("  Installing base dependencies...")
    run(f"{pip} install -r requirements/base.txt")
    print("  Installing LLM dependencies...")
    run(f"{pip} install -r requirements/llm.txt")
    print("  Installing free TTS...")
    run(f"{pip} install -r requirements/tts_free.txt")


def install_audio_deps():
    """Install platform-specific audio dependencies."""
    os_type = detect_os()
    pip = get_pip()

    if os_type == "windows":
        print("  Installing PyAudio for Windows...")
        run(f"{pip} install pyaudio")
    elif os_type == "mac":
        print("  Checking for portaudio (required for PyAudio)...")
        result = subprocess.run("brew list portaudio", shell=True, capture_output=True)
        if result.returncode != 0:
            print("  portaudio not found. Install it with:")
            print("    brew install portaudio")
            response = input("  Install portaudio now? (y/n): ").strip().lower()
            if response == "y":
                run("brew install portaudio")
        run(f"{pip} install pyaudio")
    else:
        print("  Checking for portaudio (required for PyAudio)...")
        result = subprocess.run("dpkg -l portaudio19-dev", shell=True, capture_output=True)
        if result.returncode != 0:
            print("  portaudio19-dev not found. Install it with:")
            print("    sudo apt install portaudio19-dev")
            response = input("  Install portaudio19-dev now? (y/n): ").strip().lower()
            if response == "y":
                run("sudo apt install -y portaudio19-dev")
        run(f"{pip} install pyaudio")

    # pygame for audio playback
    run(f"{pip} install pygame")
    # SpeechRecognition for STT providers
    run(f"{pip} install SpeechRecognition")


def install_optional():
    """Interactively install optional heavy dependencies."""
    pip = get_pip()

    print("\n  Optional components:")
    print("  " + "-" * 40)

    # Whisper local
    response = input("  Install Whisper local STT? (~150MB download) (y/n): ").strip().lower()
    if response == "y":
        run(f"{pip} install -r requirements/stt_whisper.txt")

    # Coqui TTS
    response = input("  Install Coqui TTS? (neural voices, ~1GB download) (y/n): ").strip().lower()
    if response == "y":
        run(f"{pip} install -r requirements/tts_coqui.txt")

    # Vosk
    response = input("  Install Vosk STT? (lightweight offline) (y/n): ").strip().lower()
    if response == "y":
        run(f"{pip} install -r requirements/stt_vosk.txt")

    # Cloud TTS
    response = input("  Install cloud TTS providers? (Google Cloud, ElevenLabs) (y/n): ").strip().lower()
    if response == "y":
        run(f"{pip} install -r requirements/tts_cloud.txt")


def generate_config():
    """Generate config.yaml from template if it doesn't exist."""
    if Path("config.yaml").exists():
        print("  config.yaml already exists, skipping")
        return

    print("  Generating config.yaml...")
    # Use the Python config module
    venv_python = "venv/Scripts/python" if detect_os() == "windows" else "venv/bin/python"
    run(f'{venv_python} -c "from phoneybaloney.config import generate_default_config; generate_default_config(\'config.yaml\')"')


def create_directories():
    """Ensure required directories exist."""
    for d in ["scenarios", "transcripts"]:
        Path(d).mkdir(exist_ok=True)
    print("  Directories ready")


def run_validation():
    """Validate the installation."""
    venv_python = "venv/Scripts/python" if detect_os() == "windows" else "venv/bin/python"
    print("  Validating installation...")
    result = subprocess.run(
        f'{venv_python} -c "import phoneybaloney; print(f\'PhoneyBaloney v{{phoneybaloney.__version__}} installed successfully\')"',
        shell=True, capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  {result.stdout.strip()}")
        return True
    else:
        print(f"  Validation failed: {result.stderr.strip()}")
        return False


def print_instructions():
    """Print OS-specific launch instructions."""
    os_type = detect_os()
    print()
    print("=" * 44)
    print("  Setup Complete!")
    print()
    if os_type == "windows":
        print("  To start PhoneyBaloney:")
        print("    Double-click start.bat")
        print()
        print("  Or from the terminal:")
        print(r"    venv\Scripts\activate")
        print("    python -m phoneybaloney")
    else:
        print("  To start PhoneyBaloney:")
        print("    ./start.sh")
        print()
        print("  Or from the terminal:")
        print("    source venv/bin/activate")
        print("    python -m phoneybaloney")
    print()
    print("  Your browser will open automatically.")
    print("=" * 44)
    print()


def main():
    print()
    print("PhoneyBaloney Setup")
    print("=" * 44)
    print()

    # Step 1: Check Python
    print("[1/8] Checking Python version...")
    check_python_version()

    # Step 2: Detect OS
    os_type = detect_os()
    print(f"[2/8] Detected OS: {os_type}")

    # Step 3: Create venv
    print("[3/8] Setting up virtual environment...")
    create_venv()

    # Step 4: Install base deps
    print("[4/8] Installing base dependencies...")
    install_base()

    # Step 5: Platform audio deps
    print("[5/8] Installing audio dependencies...")
    install_audio_deps()

    # Step 6: Optional deps
    print("[6/8] Optional dependencies...")
    install_optional()

    # Step 7: Generate config
    print("[7/8] Generating configuration...")
    generate_config()
    create_directories()

    # Step 8: Validate
    print("[8/8] Validating installation...")
    if run_validation():
        print_instructions()
    else:
        print("\nSetup completed with warnings. Some features may not work.")
        print_instructions()


if __name__ == "__main__":
    main()

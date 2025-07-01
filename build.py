#!/usr/bin/env python3.13
"""
Build script for creating executable from pyproject.toml configuration
"""

import subprocess
import sys
import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python versions
    except ImportError:
        print("Please install tomli: pip install tomli")
        sys.exit(1)


def load_pyproject_config():
    """Load PyInstaller configuration from pyproject.toml"""
    try:
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        return config.get("tool", {}).get("pyinstaller", {})
    except FileNotFoundError:
        print("pyproject.toml not found!")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        sys.exit(1)


def build_executable():
    """Build executable using PyInstaller with pyproject.toml configuration"""
    config = load_pyproject_config()

    if not config:
        print("No [tool.pyinstaller] section found in pyproject.toml")
        sys.exit(1)

    # Build PyInstaller command
    cmd = [sys.executable, "-m", "PyInstaller"]

    # Basic options
    script = config.get("script", "main.py")
    if not os.path.exists(script):
        print(f"Script {script} not found!")
        sys.exit(1)

    # Add flags based on configuration
    if config.get("onefile", False):
        cmd.append("--onefile")

    if config.get("console", True):
        cmd.append("--console")
    else:
        cmd.append("--windowed")

    # Name
    name = config.get("name")
    if name:
        cmd.extend(["--name", name])

    # Icon
    icon = config.get("icon")
    if icon and os.path.exists(icon):
        cmd.extend(["--icon", icon])
    elif icon:
        print(f"Warning: Icon file {icon} not found, skipping...")

    # Hidden imports
    hidden_imports = config.get("hidden_imports", [])
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # Data files
    datas = config.get("datas", [])
    for data in datas:
        if isinstance(data, list) and len(data) == 2:
            cmd.extend(["--add-data", f"{data[0]}{os.pathsep}{data[1]}"])

    # Excludes
    excludes = config.get("excludes", [])
    for exclude in excludes:
        cmd.extend(["--exclude-module", exclude])

    # Debug mode
    if config.get("debug", False):
        cmd.append("--debug=all")

    # Strip (Linux/Mac only)
    if config.get("strip", False) and sys.platform != "win32":
        cmd.append("--strip")

    # UPX compression
    if config.get("upx", False):
        cmd.append("--upx-dir=upx")  # Assumes UPX is in upx/ directory

    # Clean previous build
    cmd.append("--clean")

    # Add the script at the end
    cmd.append(script)

    print("Building executable with command:")
    print(" ".join(cmd))
    print()

    # Run PyInstaller
    try:
        result = subprocess.run(cmd, check=True)
        print("\nBuild completed successfully!")

        # Show output location
        dist_dir = Path("dist")
        if dist_dir.exists():
            executables = list(dist_dir.glob("*"))
            if executables:
                print(f"Executable created: {executables[0]}")

    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nBuild interrupted by user")
        sys.exit(1)


def main():
    """Main function"""
    print("🔨 Building executable from pyproject.toml configuration...")
    print()

    # Check if PyInstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller not found. Install it with:")
        print("   pip install pyinstaller")
        print("   or")
        print("   pip install -e '.[build]'")
        sys.exit(1)

    build_executable()


if __name__ == "__main__":
    main()


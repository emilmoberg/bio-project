#!/usr/bin/env python
import os
import sys
import subprocess
import platform

def run_command(command, cwd=None):
    """Runs a command and exits if it fails."""
    print(f"Running: {' '.join(command)} (in {cwd or os.getcwd()})")
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0:
        print(f"Command {' '.join(command)} failed with return code {result.returncode}")
        sys.exit(result.returncode)

def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    
    # === 1. Set up the backend virtual environment ===
    backend_dir = os.path.join(root_dir, "backend")
    venv_dir = os.path.join(backend_dir, "venv")

    # Create virtual environment if it doesn't already exist
    if not os.path.isdir(venv_dir):
        print("Creating virtual environment for backend...")
        run_command([sys.executable, "-m", "venv", "venv"], cwd=backend_dir)
    else:
        print("Virtual environment already exists.")

    # Determine the pip executable path (platform-specific)
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")

    # === 2. Install backend dependencies ===
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    if os.path.isfile(requirements_file):
        print("Installing backend Python dependencies...")
        run_command([pip_path, "install", "-r", "requirements.txt"], cwd=backend_dir)
    else:
        print("requirements.txt not found in backend directory.")
    
    # === 3. Install frontend dependencies ===
    frontend_dir = os.path.join(root_dir, "frontend")
    if os.path.isdir(frontend_dir):
        print("Installing frontend Node.js dependencies...")
        run_command(["npm", "install"], cwd=frontend_dir)
    else:
        print("Frontend directory not found.")
    
    print("Setup complete!")

if __name__ == "__main__":
    main()

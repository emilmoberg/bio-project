#!/usr/bin/env python
import os
import sys
import subprocess
import signal
import platform

def get_venv_python(backend_dir):
    """
    Returns the path to the Python interpreter inside the venv.
    """
    venv_dir = os.path.join(backend_dir, "venv")
    if platform.system() == "Windows":
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_exe = os.path.join(venv_dir, "bin", "python")
    if not os.path.isfile(python_exe):
        print("Error: Python interpreter not found in virtual environment.")
        sys.exit(1)
    return python_exe

def run_command(command, cwd):
    """
    Start a subprocess with the given command in the specified working directory.
    Returns the subprocess.Popen object.
    """
    print(f"Running: {' '.join(command)} (in {cwd})")
    return subprocess.Popen(command, cwd=cwd)

def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    # Determine the venv's Python interpreter for the backend
    backend_python = get_venv_python(backend_dir)

    # Command to start the backend dev server using uvicorn from within the venv.
    backend_cmd = [
        backend_python, "-m", "uvicorn", "main:app", "--reload"
    ]
    print("Starting backend server using venv Python...")
    backend_proc = run_command(backend_cmd, backend_dir)

    # Command to start the frontend dev server using npm.
    frontend_cmd = ["npm", "run", "dev"]
    print("Starting frontend server...")
    frontend_proc = run_command(frontend_cmd, frontend_dir)

    # Define a signal handler to terminate both processes when the script is interrupted.
    def terminate_processes(signum, frame):
        print("\nTerminating servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, terminate_processes)
    signal.signal(signal.SIGTERM, terminate_processes)

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        terminate_processes(None, None)

if __name__ == "__main__":
    main()

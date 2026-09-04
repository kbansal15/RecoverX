"""
Unified Launcher for RecoverX.
Starts the FastAPI Python backend and the React Vite frontend concurrently.
"""

import subprocess
import sys
import os
import signal
import time
import socket
import urllib.request
from pathlib import Path

# Prevent UnicodeEncodeError on Windows CP1252 consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def check_existing_backend() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=1.0) as res:
            return res.status == 200
    except Exception:
        return False

def kill_proc_tree(proc):
    if proc and proc.poll() is None:
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True,
                    timeout=5
                )
            else:
                proc.terminate()
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

def main():
    print("=" * 65)
    print("  [*] Starting RecoverX -- AI Revenue Recovery Agent")
    print("  [>] Backend:  http://localhost:8000")
    print("  [>] Frontend: http://localhost:5173")
    print("  [>] Swagger:  http://localhost:8000/docs")
    print("=" * 65)

    backend_proc = None
    if is_port_in_use(8000):
        if check_existing_backend():
            print("  [i] Existing RecoverX backend is already running and healthy.")
        else:
            print("  [!] Port 8000 is occupied by another process.")
            print("      Waiting 2s to check if it frees up...")
            time.sleep(2)
            if is_port_in_use(8000) and not check_existing_backend():
                print("  [X] Error: Port 8000 is in use by another application.")
                print("      Please stop the process on port 8000 and try again.")
                sys.exit(1)

    if not is_port_in_use(8000):
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
            cwd=ROOT_DIR / "backend"
        )
        time.sleep(1.5)
        if backend_proc.poll() is not None:
            print(f"  [X] Error: Backend process failed to start (exit code {backend_proc.returncode}).")
            sys.exit(1)
        print("  [+] Backend started successfully.")

    frontend_proc = subprocess.Popen(
        ["npm.cmd" if os.name == "nt" else "npm", "run", "dev", "--", "--port", "5173"],
        cwd=ROOT_DIR / "frontend"
    )
    print("  [+] Frontend dev server started.")

    def shutdown(signum=None, frame=None):
        print("\n[Shutdown] Stopping servers cleanly...")
        if backend_proc:
            kill_proc_tree(backend_proc)
        kill_proc_tree(frontend_proc)
        print("[Shutdown] All processes stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            if backend_proc and backend_proc.poll() is not None:
                print(f"\n[!] Backend process exited with code {backend_proc.returncode}.")
                shutdown()
            if frontend_proc.poll() is not None:
                print(f"\n[!] Frontend process exited with code {frontend_proc.returncode}.")
                shutdown()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()

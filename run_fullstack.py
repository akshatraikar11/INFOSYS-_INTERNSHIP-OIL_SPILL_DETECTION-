import os
import sys
import time
import subprocess
import webbrowser
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(ROOT_DIR, "deepspill-venv", "Scripts", "python.exe")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

processes = []

def cleanup(*args):
    print("\nShutting down DeepSpill services...")
    for p in processes:
        try:
            p.terminate()
            p.kill()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

print("DeepSpill Full-Stack Supervisor")
print("FastAPI (:8000) | Express (:3001) | Vite (:5173)\n")

# Start FastAPI Inference
print("[1/3] Starting FastAPI inference service on http://127.0.0.1:8000...")
cmd_fastapi = [
    VENV_PYTHON, "-m", "uvicorn", "inference.server:app",
    "--host", "127.0.0.1", "--port", "8000"
]
p_fastapi = subprocess.Popen(cmd_fastapi, cwd=ROOT_DIR)
processes.append(p_fastapi)

time.sleep(3)

# Start Express Backend
print("[2/3] Starting Express backend on http://localhost:3001...")
cmd_backend = ["npm.cmd" if os.name == "nt" else "npm", "start"]
p_backend = subprocess.Popen(cmd_backend, cwd=BACKEND_DIR, shell=True)
processes.append(p_backend)

time.sleep(2)

# Start Vite Frontend
print("[3/3] Starting Vite frontend on http://localhost:5173...")
cmd_frontend = ["npm.cmd" if os.name == "nt" else "npm", "run", "dev"]
p_frontend = subprocess.Popen(cmd_frontend, cwd=FRONTEND_DIR, shell=True)
processes.append(p_frontend)

time.sleep(3)
print("\nServices running. Opening http://localhost:5173 in browser.")
print("Press Ctrl+C to terminate all services.\n")

try:
    webbrowser.open("http://localhost:5173")
except Exception:
    pass

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    cleanup()

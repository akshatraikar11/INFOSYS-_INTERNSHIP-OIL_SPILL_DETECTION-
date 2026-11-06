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
    print("\n🛑 Shutting down DeepSpill Full-Stack services...")
    for p in processes:
        try:
            p.terminate()
            p.kill()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

print("=" * 75)
print("  🌊 DEEPSPILL AI: 3-TIER ENTERPRISE FULL-STACK LAUNCHER")
print("  FastAPI Inference (8000) + Express Backend (3001) + React Vite (5173)")
print("=" * 75)

# 1. Launch FastAPI Inference
print("\n[1/3] 🚀 Launching FastAPI Inference Microservice on http://127.0.0.1:8000 ...")
cmd_fastapi = [
    VENV_PYTHON, "-m", "uvicorn", "inference.server:app",
    "--host", "127.0.0.1", "--port", "8000"
]
p_fastapi = subprocess.Popen(cmd_fastapi, cwd=ROOT_DIR)
processes.append(p_fastapi)

time.sleep(3)

# 2. Launch Express Backend
print("[2/3] 🚀 Launching Express Backend API Gateway on http://localhost:3001 ...")
cmd_backend = ["npm.cmd" if os.name == "nt" else "npm", "start"]
p_backend = subprocess.Popen(cmd_backend, cwd=BACKEND_DIR, shell=True)
processes.append(p_backend)

time.sleep(2)

# 3. Launch React Frontend
print("[3/3] 🚀 Launching React (Vite) Production Dashboard on http://localhost:5173 ...")
cmd_frontend = ["npm.cmd" if os.name == "nt" else "npm", "run", "dev"]
p_frontend = subprocess.Popen(cmd_frontend, cwd=FRONTEND_DIR, shell=True)
processes.append(p_frontend)

time.sleep(3)
print("\n" + "=" * 75)
print("  ✅ All 3 tiers are online!")
print("  🌐 Opening Mission Control Dashboard: http://localhost:5173")
print("  💡 Press Ctrl+C at any time in this window to stop all services.")
print("=" * 75 + "\n")

try:
    webbrowser.open("http://localhost:5173")
except Exception:
    pass

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    cleanup()


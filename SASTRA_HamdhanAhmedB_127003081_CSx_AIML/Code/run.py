import os
import socket
import subprocess
import sys
import time

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def start_services():
    print("=" * 60)
    print("AUTOSAR AI — Starting Services...")
    print("=" * 60)
    
    processes = []
    
    # Check Backend (port 8000)
    if is_port_in_use(8000):
        print("[INFO] Backend API is already running on http://127.0.0.1:8000")
    else:
        print("[START] Launching Backend API server on http://127.0.0.1:8000...")
        backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
        backend_proc = subprocess.Popen(backend_cmd)
        processes.append(("Backend", backend_proc))
        
        # Wait for backend to be ready
        for _ in range(15):
            time.sleep(0.5)
            if is_port_in_use(8000):
                print("[READY] Backend is listening on port 8000.")
                break
    
    # Check Frontend (port 8501)
    if is_port_in_use(8501):
        print("[INFO] Frontend Streamlit UI is already running on http://localhost:8501")
    else:
        print("[START] Launching Frontend Streamlit UI on http://localhost:8501...")
        frontend_cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"]
        frontend_proc = subprocess.Popen(frontend_cmd)
        processes.append(("Frontend", frontend_proc))
    
    if not processes:
        print("[READY] Both Backend and Frontend are already active and running!")
        return

    print("=" * 60)
    print("Application is active! Press Ctrl+C to stop launched services.")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"[WARN] {name} process exited with code {proc.returncode}.")
                    return
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down launched services...")
        for name, proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        print("[DONE] Shutdown complete.")

if __name__ == "__main__":
    start_services()


import subprocess
import time
import os
import sys
import webview
def start():
    backend = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
    print("🚀 Starting FastAPI backend...")
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
        cwd=backend,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)
    url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    print(f"🌐 Opening BOQ AI at {url}")
    webview.create_window("BOQ AI System", url, width=1280, height=800)
    webview.start()
if __name__ == "__main__":
    start()

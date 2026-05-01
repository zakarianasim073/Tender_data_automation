import subprocess, time, os, sys, webview
def start():
    backend = os.path.join(os.path.dirname(__file__), "..", "backend")
    subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"], cwd=backend)
    time.sleep(3)
    webview.create_window("BOQ AI", os.getenv("FRONTEND_URL", "http://localhost:5173"), width=1280, height=800)
    webview.start()
if __name__ == "__main__":
    start()

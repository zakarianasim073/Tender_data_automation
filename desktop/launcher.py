import subprocess
import time
import os
import sys
import webview
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DesktopLauncher")

def start():
    # Production check: if a URL is provided, use it directly
    prod_url = os.getenv("BOQ_AI_URL")

    if not prod_url:
        backend = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
        logger.info("🚀 Starting local FastAPI backend for desktop...")
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
            cwd=backend,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(3)
        url = "http://localhost:8000" # Local mode usually bundles frontend or proxies
    else:
        url = prod_url

    logger.info(f"🌐 Opening BOQ AI at {url}")
    webview.create_window("BOQ AI System - Professional Edition", url, width=1280, height=800)
    webview.start()

if __name__ == "__main__":
    start()

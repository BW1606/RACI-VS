"""
Desktop launcher for RACI-VS Manager.

Starts the FastAPI server in a background thread, opens the browser, and
keeps a Windows system-tray icon running so the user can reopen or quit
the app without touching a terminal.

Build with build.bat (PyInstaller). For development, run directly:
    python launcher.py
"""

import ctypes
import logging
import os
import sys
import threading
import time
import webbrowser

import pystray
import uvicorn
from PIL import Image

PORT = 8000
URL = f"http://127.0.0.1:{PORT}"

# Log to %APPDATA%\RACI-VS\error.log so problems are diagnosable without a terminal
_log_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "RACI-VS")
os.makedirs(_log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(_log_dir, "error.log"),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)


def _alert(message: str) -> None:
    """Show a Windows error popup — no terminal required."""
    ctypes.windll.user32.MessageBoxW(0, message, "RACI-VS — Startup Error", 0x10)


def _run_server() -> None:
    try:
        uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_level="warning")
    except Exception as exc:
        logging.exception("Server failed to start")
        _alert(
            f"The server failed to start and the app cannot run.\n\n"
            f"Error: {exc}\n\n"
            f"Full details: {os.path.join(_log_dir, 'error.log')}"
        )
        os._exit(1)


def _open_browser() -> None:
    time.sleep(2.0)  # give uvicorn time to bind the port
    webbrowser.open(URL)


def _make_tray_image() -> Image.Image:
    img = Image.new("RGB", (64, 64), color=(0, 102, 204))
    return img


def _on_open(_icon: pystray.Icon, _item: pystray.MenuItem) -> None:
    webbrowser.open(URL)


def _on_quit(icon: pystray.Icon, _item: pystray.MenuItem) -> None:
    icon.stop()
    os._exit(0)


def main() -> None:
    threading.Thread(target=_run_server,   daemon=True).start()
    threading.Thread(target=_open_browser, daemon=True).start()

    menu = pystray.Menu(
        pystray.MenuItem("Open RACI-VS", _on_open, default=True),
        pystray.MenuItem("Quit",         _on_quit),
    )
    icon = pystray.Icon("RACI-VS", _make_tray_image(), "RACI-VS Manager", menu)
    icon.run()


if __name__ == "__main__":
    main()

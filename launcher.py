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
import traceback
import webbrowser

import pystray
import uvicorn
from PIL import Image
from main import app as fastapi_app

PORT = 8000
URL = f"http://127.0.0.1:{PORT}"

LOG_PATH = os.path.join(os.path.dirname(sys.executable), "raci_vs.log")

# File-based log config: no StreamHandler so sys.stdout.isatty() is never called.
# Captures all uvicorn output to LOG_PATH for post-mortem debugging.
UVICORN_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"()": "logging.Formatter", "fmt": "%(asctime)s %(levelname)s %(message)s"},
        "access":  {"()": "logging.Formatter", "fmt": "%(asctime)s %(levelname)s %(message)s"},
    },
    "handlers": {
        "default": {"class": "logging.FileHandler", "filename": LOG_PATH, "formatter": "default"},
        "access":  {"class": "logging.FileHandler", "filename": LOG_PATH, "formatter": "access"},
    },
    "loggers": {
        "uvicorn":        {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error":  {"handlers": ["default"], "level": "INFO"},
        "uvicorn.access": {"handlers": ["access"],  "level": "INFO", "propagate": False},
    },
}


def _show_error(msg: str) -> None:
    ctypes.windll.user32.MessageBoxW(0, msg, "RACI-VS — Server Error", 0x10)


def _run_server() -> None:
    # Redirect stdout/stderr to the log file so any print() or raw stderr output
    # from app code or PyInstaller internals is captured.
    log_file = open(LOG_PATH, "w", buffering=1, encoding="utf-8")
    sys.stdout = log_file
    sys.stderr = log_file
    log_file.write(f"=== RACI-VS server starting ===\n")

    try:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=PORT, log_config=UVICORN_LOG_CONFIG)
    except BaseException:
        tb = traceback.format_exc()
        log_file.write(tb)
        _show_error(tb)


def _open_browser() -> None:
    time.sleep(1.5)  # give uvicorn time to bind the port
    webbrowser.open(URL)


def _make_tray_image() -> Image.Image:
    """Generate a simple coloured square as the tray icon."""
    img = Image.new("RGB", (64, 64), color=(0, 102, 204))
    return img


def _on_open(_icon: pystray.Icon, _item: pystray.MenuItem) -> None:
    webbrowser.open(URL)


def _on_quit(icon: pystray.Icon, _item: pystray.MenuItem) -> None:
    icon.stop()
    os._exit(0)  # kills the daemon uvicorn thread cleanly


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

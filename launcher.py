"""
Desktop launcher for RACI-VS Manager.

Starts the FastAPI server in a background thread, opens the browser, and
keeps a Windows system-tray icon running so the user can reopen or quit
the app without touching a terminal.

Build with build.bat (PyInstaller). For development, run directly:
    python launcher.py
"""

import ctypes
import os
import sys
import threading
import time
import traceback
import webbrowser

import pystray
import uvicorn
from PIL import Image

PORT = 8000
URL = f"http://127.0.0.1:{PORT}"


def _show_error(msg: str) -> None:
    ctypes.windll.user32.MessageBoxW(0, msg, "RACI-VS — Server Error", 0x10)


def _run_server() -> None:
    try:
        # log_config=None prevents uvicorn's default formatter from calling
        # sys.stdout.isatty(), which crashes when built with --noconsole (stdout is None)
        uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_config=None)
    except Exception:
        _show_error(traceback.format_exc())


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

import os
import sys


def resource_path(relative: str) -> str:
    """Resolve a path to a bundled asset, works both in source and PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

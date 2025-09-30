import json
import os
from PyQt5.QtCore import QStandardPaths

# Default settings
settings_file = "settings.json"

# Get user’s Downloads folder in a cross-platform way
download_folder = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)

# Fallback if Downloads not available → use Documents
if not download_folder:
    download_folder = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)

settings = {
    "default_path": download_folder,
    "default_quality": "720p",
    "cookiefile": r"YouTubeDownloader\Cookie\youtube.com_cookies.txt",  # relative path inside installer
    "ffmpeg_path": r"YouTubeDownloader\ffmpeg\bin\ffmpeg.exe"  # relative path inside installer
}

def save_settings():
    """Save current settings to settings.json"""
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)

# Load settings automatically if file exists
if os.path.exists(settings_file):
    try:
        with open(settings_file, "r") as f:
            loaded = json.load(f)
            settings.update(loaded)
    except Exception:
        # if settings file broken, ignore and keep defaults
        pass

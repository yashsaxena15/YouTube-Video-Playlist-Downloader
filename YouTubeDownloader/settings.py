import json
import os

# Default settings
settings_file = "settings.json"
settings = {
    "default_path": os.path.expanduser("~/Downloads"),
    "default_quality": "720p",
    "cookiefile": r"D:\yash\GUI yt playlist\YouTubeDownloader\Cookie\youtube.com_cookies.txt",  # path to cookies.txt
    "ffmpeg_path": r"D:\yash\GUI yt playlist\YouTubeDownloader\ffmpeg\bin\ffmpeg.exe"  # optional bundled ffmpeg path
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

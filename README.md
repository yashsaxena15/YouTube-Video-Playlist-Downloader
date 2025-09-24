# YouTube Playlist Downloader 🎬

A **Python-based desktop application** for downloading YouTube videos and playlists with support for high-resolution video (up to 8K) and high-quality audio (up to 320kbps). Built with **PyQt5** for a sleek GUI and **yt-dlp** for fast and reliable downloads.

---

## Features

- Download **single videos or entire playlists** from YouTube.
- Choose **video quality**: 360p, 480p, 720p, 1080p, 1440p (2K), 2160p (4K), 4320p (8K).  
- Choose **audio quality**: 128k, 192k, 256k, 320k kbps.
- Download **video + audio** or **audio only**.
- Automatic **file format selection** based on download type:
  - Video: MP4, WEBM  
  - Audio: MP3, M4A
- **Progress bars** for each video in a playlist.
- **Custom download folder** selection.
- Dark-themed, modern GUI.

---

## Screenshots

![App Screenshot](https://github.com/yashsaxena15/YouTube-Video-Playlist-Downloader/blob/master/YouTubeDownloader/assets/screenshot.png)  
![App Screenshot](https://github.com/yashsaxena15/YouTube-Video-Playlist-Downloader/blob/master/YouTubeDownloader/assets/screenshot2.png)


---

## Installation

### Windows

1. Download the latest release from the [Releases]([https://github.com/yashsaxena15/YouTube-Video-Playlist-Downloader/releases/tag/v1.0.0]) page.  
2. Extract the `.zip` file (if applicable).  
3. Run `main.exe` under dist folder.  

> No Python installation is required; the app is standalone.

### Requirements (for source code)

If running from source, make sure Python 3.12+ is installed.

```bash
pip install -r requirements.txt

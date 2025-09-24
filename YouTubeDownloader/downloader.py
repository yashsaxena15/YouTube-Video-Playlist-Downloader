from PyQt5.QtCore import QThread, pyqtSignal
import os
import yt_dlp
from settings import settings  # import cookiefile & ffmpeg_path

class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)

    def __init__(self, url, folder, quality, download_type, file_format, audio_quality, cookiefile=""):
        super().__init__()
        self.url = url
        self.folder = folder
        self.quality = quality
        self.download_type = download_type
        self.file_format = file_format
        self.audio_quality = audio_quality
        # Use provided cookiefile, otherwise fall back to settings
        self.cookiefile = cookiefile if cookiefile else settings.get("cookiefile", "")
        # ffmpeg path from settings
        self.ffmpeg_path = settings.get("ffmpeg_path", None)

    def run(self):
        # Map for video quality
        quality_height = {
            "360p": 360,
            "480p": 480,
            "720p": 720,
            "1080p": 1080,
            "1440p": 1440,  # 2K
            "2160p": 2160,  # 4K
            "4320p": 4320   # 8K
        }.get(self.quality, 720)

        try:
            # Ensure temp folder exists
            temp_path = os.path.join(self.folder, "yt_temp")
            os.makedirs(temp_path, exist_ok=True)

            # Common options
            base_opts = {
                'outtmpl': os.path.join(self.folder, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'cachedir': False,
                'noprogress': False,
                'ignoreerrors': True,
                'paths': {'temp': temp_path},  # yt-dlp way to set temp dir
            }

            # Add cookies if provided
            if self.cookiefile:
                base_opts['cookiefile'] = self.cookiefile

            # Add ffmpeg if path provided
            if self.ffmpeg_path:
                base_opts['ffmpeg_location'] = self.ffmpeg_path

            if self.download_type == "Video + Audio":
                ydl_opts = dict(base_opts)
                ydl_opts.update({
                    'format': f'bestvideo[height<={quality_height}]+bestaudio/best',
                    'merge_output_format': self.file_format.lower(),
                })
            else:  # Audio only
                ydl_opts = dict(base_opts)
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.file_format.lower(),
                        'preferredquality': self.audio_quality,
                    }],
                })

            # Start download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.progress_signal.emit("✅ All downloads completed successfully!\n")

        except Exception as e:
            self.progress_signal.emit(f"❌ Error: {str(e)}\n")

    def progress_hook(self, d):
        # Only handle downloading status
        if d.get('status') == 'downloading':
            filename = os.path.basename(d.get('filename', ''))
            percent_str = d.get('_percent_str', '0.0%').strip()
            # Remove percent sign and convert to int
            try:
                percent = int(float(percent_str.replace('%','')))
            except:
                percent = 0
            self.progress_signal.emit(f"⬇️ Downloading: {filename} - {percent}%")

        elif d.get('status') == 'finished':
            filename = os.path.basename(d.get('filename', ''))
            self.progress_signal.emit(f"✅ Finished: {filename}")

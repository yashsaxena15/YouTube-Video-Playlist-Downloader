from PyQt5.QtCore import QThread, pyqtSignal
import os
import yt_dlp
from settings import settings  # import cookiefile & ffmpeg_path

class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)   # Download progress (percentage + title)
    speed_signal = pyqtSignal(str)      # Download speed in MB/s
    size_signal = pyqtSignal(str)       # Total size of file in MB
    eta_signal = pyqtSignal(str)        # ETA as HH:MM:SS

    def __init__(self, url, folder, quality, download_type, file_format, audio_quality, cookiefile=""):
        super().__init__()
        self.url = url
        self.folder = folder
        self.quality = quality
        self.download_type = download_type
        self.file_format = file_format
        self.audio_quality = audio_quality
        self.cookiefile = cookiefile if cookiefile else settings.get("cookiefile", "")
        self.ffmpeg_path = settings.get("ffmpeg_path", None)

    def run(self):
        quality_height = {
            "360p": 360, "480p": 480, "720p": 720,
            "1080p": 1080, "1440p": 1440, "2160p": 2160, "4320p": 4320
        }.get(self.quality, 720)

        try:
            temp_path = os.path.join(self.folder, "yt_temp")
            os.makedirs(temp_path, exist_ok=True)

            base_opts = {
                'outtmpl': os.path.join(self.folder, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'cachedir': False,
                'noprogress': False,
                'ignoreerrors': True,
                'paths': {'temp': temp_path},
            }

            if self.cookiefile:
                base_opts['cookiefile'] = self.cookiefile
            if self.ffmpeg_path:
                base_opts['ffmpeg_location'] = self.ffmpeg_path

            if self.download_type == "Video + Audio":
                ydl_opts = dict(base_opts)
                ydl_opts.update({
                    'format': f'bestvideo[height<={quality_height}]+bestaudio/best',
                    'merge_output_format': self.file_format.lower(),
                })
            else:
                ydl_opts = dict(base_opts)
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.file_format.lower(),
                        'preferredquality': self.audio_quality,
                    }],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.progress_signal.emit("✅ All downloads completed successfully!\n")
            self.speed_signal.emit("0 MB/s")
            self.size_signal.emit("0 MB")
            self.eta_signal.emit("00:00:00")

        except Exception as e:
            self.progress_signal.emit(f"❌ Error: {str(e)}\n")
            self.speed_signal.emit("0 MB/s")
            self.size_signal.emit("0 MB")
            self.eta_signal.emit("00:00:00")

    def progress_hook(self, d):
        if d.get('status') == 'downloading':
            filename = os.path.basename(d.get('filename', ''))
            percent_str = d.get('_percent_str', '0.0%').strip()
            try:
                percent = int(float(percent_str.replace('%','')))
            except:
                percent = 0

            # Speed in MB/s
            speed = d.get('speed') or 0
            speed_mbps = f"{speed / 1024 / 1024:.2f} MB/s"
            self.speed_signal.emit(speed_mbps)

            # Total size in MB
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            size_mb = f"{total_bytes / 1024 / 1024:.2f} MB" if total_bytes else "Unknown"
            self.size_signal.emit(size_mb)

            # ETA calculation
            downloaded = d.get('downloaded_bytes') or 0
            if speed > 0 and total_bytes:
                remaining_bytes = total_bytes - downloaded
                eta_sec = int(remaining_bytes / speed)
                hours, rem = divmod(eta_sec, 3600)
                minutes, seconds = divmod(rem, 60)
                eta_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            else:
                eta_str = "00:00:00"
            self.eta_signal.emit(eta_str)

            self.progress_signal.emit(f"⬇️ Downloading: {filename} - {percent}%")

        elif d.get('status') == 'finished':
            filename = os.path.basename(d.get('filename', ''))
            self.progress_signal.emit(f"✅ Finished: {filename}")
            self.eta_signal.emit("00:00:00")

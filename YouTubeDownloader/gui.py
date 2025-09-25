from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QFileDialog, QVBoxLayout, QHBoxLayout,
    QProgressBar, QScrollArea
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from downloader import DownloadThread
from settings import settings, save_settings
import re
from PyQt5.QtGui import QIcon



class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        # Inside __init__ of YouTubeDownloader
        self.setWindowIcon(QIcon("assets/app_icon.ico"))
        self.setWindowTitle("YouTube Playlist Downloader")
        self.setGeometry(300, 200, 750, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0;")
        self.video_widgets = {}  # Store dict with progress bar, speed label, size label, eta label
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # --- URL Input ---
        url_layout = QHBoxLayout()
        url_label = QLabel("YouTube URL:")
        url_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube video or playlist URL...")
        self.url_input.setStyleSheet(
            "padding: 6px; font-size: 12px; color: #000000; background-color: #f0f0f0;"
        )
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # --- Download Folder ---
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Download Folder:")
        folder_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.folder_display = QLineEdit(settings["default_path"])
        self.folder_display.setReadOnly(True)
        folder_btn = QPushButton("Browse")
        folder_btn.setStyleSheet("background-color: #3a3a3a; color: white; padding: 5px;")
        folder_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_display)
        folder_layout.addWidget(folder_btn)
        layout.addLayout(folder_layout)

        # --- Download Type ---
        type_layout = QHBoxLayout()
        type_label = QLabel("Download Type:")
        type_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.download_type_combo = QComboBox()
        self.download_type_combo.addItems(["Video + Audio", "Audio Only"])
        self.download_type_combo.currentTextChanged.connect(self.update_options_visibility)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.download_type_combo)
        layout.addLayout(type_layout)

        # --- Video Quality ---
        video_quality_layout = QHBoxLayout()
        self.video_quality_label = QLabel("Video Quality:")
        self.video_quality_combo = QComboBox()
        self.video_quality_combo.addItems(
            ["360p","480p","720p","1080p","1440p","2160p","4320p"]
        )
        self.video_quality_combo.setCurrentText(settings["default_quality"])
        video_quality_layout.addWidget(self.video_quality_label)
        video_quality_layout.addWidget(self.video_quality_combo)
        layout.addLayout(video_quality_layout)

        # --- Audio Quality ---
        audio_quality_layout = QHBoxLayout()
        self.audio_quality_label = QLabel("Audio Quality:")
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["128k","192k","256k","320k"])
        audio_quality_layout.addWidget(self.audio_quality_label)
        audio_quality_layout.addWidget(self.audio_quality_combo)
        layout.addLayout(audio_quality_layout)

        # --- File Format ---
        format_layout = QHBoxLayout()
        self.file_format_label = QLabel("File Format:")
        self.file_format_combo = QComboBox()
        self.file_format_combo.addItems(["MP4","WEBM"])
        format_layout.addWidget(self.file_format_label)
        format_layout.addWidget(self.file_format_combo)
        layout.addLayout(format_layout)

        # --- Download Button ---
        self.download_btn = QPushButton("Download")
        self.download_btn.setStyleSheet(
            "background-color: #007acc; color: white; padding: 8px; font-size: 14px;"
        )
        self.download_btn.clicked.connect(self.download_clicked)
        layout.addWidget(self.download_btn, alignment=Qt.AlignCenter)

        # --- Scroll Area for per-video progress ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)
        self.update_options_visibility()

    # ---------------- Methods ----------------
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.folder_display.setText(folder)
            settings["default_path"] = folder
            save_settings()

    def update_options_visibility(self):
        download_type = self.download_type_combo.currentText()
        if download_type == "Audio Only":
            self.audio_quality_label.show()
            self.audio_quality_combo.show()
            self.video_quality_label.hide()
            self.video_quality_combo.hide()
            self.file_format_combo.clear()
            self.file_format_combo.addItems(["MP3","M4A"])
        else:
            self.video_quality_label.show()
            self.video_quality_combo.show()
            self.audio_quality_label.hide()
            self.audio_quality_combo.hide()
            self.file_format_combo.clear()
            self.file_format_combo.addItems(["MP4","WEBM"])

    def download_clicked(self):
        url = self.url_input.text()
        folder = self.folder_display.text()
        video_quality = self.video_quality_combo.currentText()
        download_type = self.download_type_combo.currentText()
        file_format = self.file_format_combo.currentText()
        audio_quality = self.audio_quality_combo.currentText()

        if not url:
            return

        self.download_btn.setEnabled(False)
        self.video_widgets.clear()

        # Clear old widgets
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Start download
        self.thread = DownloadThread(
            url, folder, video_quality, download_type,
            file_format, audio_quality,
            cookiefile=settings.get("cookiefile","")
        )
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.speed_signal.connect(self.update_speed)
        self.thread.size_signal.connect(self.update_size)
        self.thread.eta_signal.connect(self.update_eta)  # ETA signal connected properly here
        self.thread.finished.connect(lambda: self.download_btn.setEnabled(True))
        self.thread.start()

    def create_video_widgets(self, title):
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #f0f0f0;")
        
        # Progress bar
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setTextVisible(True)
        progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #00bfff;
                width: 1px;
            }
        """)
        
        # Speed, Size, ETA labels
        speed_label = QLabel("Speed: 0 MB/s")
        size_label = QLabel("Size: 0 MB")
        eta_label = QLabel("ETA: 00:00:00")
        for lbl in (speed_label, size_label, eta_label):
            lbl.setStyleSheet("color: #f0f0f0; font-size: 15px; font-weight: bold;")
        
        info_layout = QHBoxLayout()
        info_layout.addWidget(speed_label)
        info_layout.addSpacing(20)
        info_layout.addWidget(size_label)
        info_layout.addSpacing(20)
        info_layout.addWidget(eta_label)
        info_layout.addStretch()
        
        # Add progress bar and info layout
        self.scroll_layout.addWidget(title_label)
        self.scroll_layout.addWidget(progress)
        self.scroll_layout.addLayout(info_layout)
        
        self.video_widgets[title] = {
            "progress": progress,
            "speed": speed_label,
            "size": size_label,
            "eta": eta_label
        }

    def update_progress(self, message):
        if message.startswith("⬇️ Downloading:"):
            percent_match = re.search(r"(\d+(\.\d+)?)%", message)
            percent = int(float(percent_match.group(1))) if percent_match else 0

            title_part = message.replace("⬇️ Downloading: ","")
            title = title_part.split(" - ")[0].strip()

            if title not in self.video_widgets:
                self.create_video_widgets(title)

            self.video_widgets[title]["progress"].setValue(percent)

        elif message.startswith("✅ Finished:"):
            title = message.replace("✅ Finished:", "").strip()
            if title in self.video_widgets:
                self.video_widgets[title]["progress"].setValue(100)
                self.video_widgets[title]["eta"].setText("ETA: 00:00:00")  # reset ETA

    def update_speed(self, speed_msg):
        for title, widgets in self.video_widgets.items():
            widgets["speed"].setText(f"Speed: {speed_msg}")

    def update_size(self, size_msg):
        for title, widgets in self.video_widgets.items():
            widgets["size"].setText(f"Size: {size_msg}")

    def update_eta(self, eta_msg):
        for title, widgets in self.video_widgets.items():
            widgets["eta"].setText(f"ETA: {eta_msg}")

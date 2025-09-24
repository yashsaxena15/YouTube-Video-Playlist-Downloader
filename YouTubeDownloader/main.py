import sys
from PyQt5.QtWidgets import QApplication
from gui import YouTubeDownloader

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())

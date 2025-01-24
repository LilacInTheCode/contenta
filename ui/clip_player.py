import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QListWidget, QFileDialog, QLabel,
    QHBoxLayout, QSizePolicy, QSpacerItem
)
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QTime, QObject, pyqtSignal, QSize

from ui.clip_player_ui import PlayButton, PauseButton, StopButton, StartClipButton, EndClipButton, FileControlDecoration


class VideoClip(QObject):
    clip_begin = pyqtSignal(int)
    clip_end = pyqtSignal(int)
    zero_clip = pyqtSignal()

    title_set = pyqtSignal(str)

    def __init__(self, start: int | None = None, end: int | None = None, title: str = "Video Clip"):
        super().__init__()

        self.title: str = title
        if title == "":
            self.title = "Video Clip"

        self.start: int = max(start, 0)
        self.end: int = max(end, 0)
        if self.start > self.end:
            self.start = self.end

    def beginClip(self, start: int):
        self.start = max(start, 0)
        if self.end < self.start:
            self.end = self.start

        self.clip_begin.emit(self. start)
        if self.end == self.start:
            self.zero_clip()

    def endClip(self, end: int):
        self.end = max(end, 0)
        if self.start > self.end:
            self.start = self.end

    def setTitle(self, title: str):
        if not title == "":
            self.title = title

    def getBounds(self) -> (int, int):
        return self.start, self.end

    def getTitle(self) -> str:
        return self.title

    def duration(self) -> int:
        if self.start is None or self.end is None:
            return -1
        return self.end - self.start


class ReferenceVideo(QObject):
    def __init__(self):
        super().__init__()

        self.filename: str | None = None
        self.mediaPlayer: QMediaPlayer | None = None
        self.clips: dict[int, VideoClip] = {}

    def setVideoRef(self, filename: str):
        pass

    def newClip(self, clip: VideoClip):
        if self.filename is None: return
        if clip is None: return
        if clip.duration() < 0: return

        self.clips[1] = clip


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 Video Player")
        self.setGeometry(100, 100, 800, 600)

        widget = QWidget(self)
        self.setCentralWidget(widget)

        self.videoWidget = QVideoWidget()
        self.videoWidget.setMinimumSize(640, 480)
        self.mediaPlayer = QMediaPlayer(None)

        self.playButton = PlayButton()
        self.playButton.clicked.connect(self.play_video)
        self.pauseButton = PauseButton()
        self.pauseButton.clicked.connect(self.pause_video)
        self.stopButton = StopButton()
        self.stopButton.clicked.connect(self.stop_video)
        self.startClipButton = StartClipButton()
        self.startClipButton.toggled.connect(self.start_clip)
        self.endClipButton = EndClipButton()
        self.endClipButton.clicked.connect(self.end_clip)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.slider.sliderMoved.connect(self.set_position)

        self.clipListWidget = QListWidget()
        self.clipListWidget.clicked.connect(self.select_clip)

        self.importButton = QPushButton("Import Video")
        self.importButton.clicked.connect(self.import_video)
        spacer = FileControlDecoration()
        spacer.setMinimumWidth(400)
        self.exportButton = QPushButton("Export Clips")
        self.exportButton.clicked.connect(self.export_clips)

        self.currentClipStart = None
        self.clips = []

        playerLayout = QVBoxLayout()

        playerLayout.addWidget(self.videoWidget)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.pauseButton)
        controlLayout.addWidget(self.stopButton)
        controlLayout.addWidget(self.startClipButton)
        controlLayout.addWidget(self.slider)
        controlLayout.addWidget(self.endClipButton)

        fileControlLayout = QHBoxLayout()
        fileControlLayout.addWidget(self.importButton)
        fileControlLayout.addWidget(spacer)
        fileControlLayout.addWidget(self.exportButton)

        playerLayout.addLayout(controlLayout)

        layout = QVBoxLayout()
        layout.addLayout(fileControlLayout)

        layout.addLayout(playerLayout)
        layout.addWidget(QLabel("Clips:"))
        layout.addWidget(self.clipListWidget)

        widget.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def import_video(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
        if fileName:
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.mediaPlayer.setVideoOutput(self.videoWidget)
            self.videoWidget.show()
            self.play_video()
            self.clips.append((0, self.mediaPlayer.duration()))
            self.clipListWidget.addItem(f"Full Video: {self.format_time(0)} - {self.format_time(self.mediaPlayer.duration())}")

    def export_clips(self):
        pass

    @staticmethod
    def format_time(ms):
        return QTime(0, 0).addMSecs(ms).toString("hh:mm:ss")

    def play_video(self):
        # Enable and activate play button
        self.playButton.setEnabled(True)
        self.playButton.setChecked(True)
        # Enable but don't activate pause button
        self.pauseButton.setEnabled(True)
        self.pauseButton.setChecked(False)
        # Enable the stop button
        self.stopButton.setEnabled(True)

        # Start playing video
        self.mediaPlayer.play()

    def pause_video(self):
        if self.mediaPlayer.isPlaying():
            # Deactivate play button
            self.playButton.setChecked(False)
            # Activate pause button
            self.pauseButton.setChecked(True)
            # Pause the video
            self.mediaPlayer.pause()
        else:
            # Resume if already paused
            self.play_video()

    def stop_video(self):
        self.stopButton.setEnabled(False)

        self.playButton.setChecked(False)

        self.pauseButton.setChecked(False)
        self.pauseButton.setEnabled(False)

        self.mediaPlayer.stop()

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def start_clip(self):
        if self.startClipButton.isChecked():
            self.currentClipStart = self.mediaPlayer.position()
            self.endClipButton.setEnabled(True)
        else:
            self.currentClipStart = None
            self.endClipButton.setEnabled(False)

    def end_clip(self):
        if self.currentClipStart is not None:
            end = self.mediaPlayer.position()
            self.clips.append((self.currentClipStart, end))
            self.clipListWidget.addItem(f"Clip: {self.format_time(self.currentClipStart)} - {self.format_time(end)}")
            self.currentClipStart = None

        self.endClipButton.setEnabled(False)
        self.startClipButton.setChecked(False)

    def select_clip(self):
        selectedClip = self.clipListWidget.currentRow()
        if 0 <= selectedClip < len(self.clips):
            start, end = self.clips[selectedClip]
            self.mediaPlayer.setPosition(start)
            self.slider.setRange(start, end)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import (
    QPushButton, QSizePolicy, QWidget
)


class SquareControlButton(QPushButton):
    def __init__(self, label: str):
        super().__init__(label)

        self.setMaximumSize(32, 32)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setEnabled(False)


class PlayButton(SquareControlButton):
    def __init__(self):
        super().__init__("▶")
        self.setToolTip("Play")
        self.setCheckable(True)


class PauseButton(SquareControlButton):
    def __init__(self):
        super().__init__("⏸")
        self.setToolTip("Pause")
        self.setCheckable(True)


class StopButton(SquareControlButton):
    def __init__(self):
        super().__init__("⏹")
        self.setToolTip("Stop")


class StartClipButton(SquareControlButton):
    def __init__(self):
        super().__init__("⏺")
        self.setToolTip("Start Clip")
        self.setCheckable(True)

        self.toggled.connect(self.on_toggle)

    def on_toggle(self):
        if self.isChecked():
            self.setToolTip("Cancel")
            self.setText("x")
        else:
            self.setToolTip("Start Clip")
            self.setText("⏺")


class EndClipButton(SquareControlButton):
    def __init__(self):
        super().__init__("🎞")
        self.setToolTip("End Clip")

class FileControlDecoration(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

    def paintEvent(self, a0):
        p = QPainter(self)
        p.setPen(QPen(Qt.GlobalColor.lightGray, 1))
        area = self.rect().adjusted(4, 0, 4, 0)
        left_margin = int(area.width() * 0.333)
        right_margin = int(area.width() - left_margin)
        midline = int(area.height() / 2)
        p.drawLine(QPoint(area.left(), midline),
                   QPoint(left_margin, midline))
        p.drawLine(QPoint(area.right(), midline),
                   QPoint(right_margin, midline))
        p.drawLine(QPoint(left_margin, midline),
                   QPoint(left_margin, area.bottom()))
        p.drawLine(QPoint(right_margin, midline),
                   QPoint(right_margin, area.bottom()))
from PyQt6.QtWidgets import (
    QPushButton, QSizePolicy
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

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import (
    QFont, QTextOption, QTextCursor, QTextCharFormat, QColor
)

from editor.cscr import CSCRFile


class TextArea(QPlainTextEdit):
    script_updated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
         # self.section_offsets = []  # Track section positions

        self.setWordWrapMode(
            QTextOption.WrapMode.WordWrap)  # QTextOption.WordWrap (Wrap at word boundaries)
        self.setFont(QFont("Courier", 12, weight=QFont.Weight.Black))  # Monospace font
        self.setLineWidth(80)  # Approximate 80-character width

        self.textChanged.connect(self.text_changed)

    def render_script(self, script: CSCRFile):
        if script is None: return

        self.blockSignals(True)

        # Set text in editor
        self.setPlainText(script.content)
        self.apply_formatting(script.section_offsets)

        self.blockSignals(False)

    def apply_formatting(self, offset_map: list[(str, int, int, int)]):
        """Applies visual formatting to section headers."""
        cursor = QTextCursor(self.document())
        fmt_header = QTextCharFormat()
        fmt_header.setForeground(QColor(255, 0, 0, 255))
        fmt_header.setBackground(QColor(0, 0, 0, 255))
        fmt_header.setFontWeight(600)

        for element_id, header_len, start, end in offset_map:
            cursor.setPosition(start - header_len)  # Position at the header
            print(f"Cursor start: {cursor.position()}")
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, header_len)
            print(f"Cursor end: {cursor.position()}")
            cursor.mergeCharFormat(fmt_header)

    def text_changed(self):
        """Emit the new text buffer."""
        self.script_updated.emit(self.toPlainText())


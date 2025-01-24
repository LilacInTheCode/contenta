from typing import override

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import (
    QFont, QTextOption, QTextCursor, QTextCharFormat, QColor
)

from ui.menus import HeaderContextMenu

from editor.cscr import CSCRTree


class TextArea(QPlainTextEdit):
    script_updated = pyqtSignal(str, str)
    header_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.readable_offsets: dict[str, (int, int, int)] = {}  # Track section positions

        self.setWordWrapMode(
            QTextOption.WrapMode.WordWrap)  # QTextOption.WordWrap (Wrap at word boundaries)
        self.setFont(QFont("VT323", 14, weight=QFont.Weight.Black))  # Monospace font
        self.setLineWidth(80)  # Approximate 80-character width

        self.debouncer = QTimer()
        self.debouncer.setSingleShot(True)
        self.debouncer.setInterval(500)
        self.debouncer.timeout.connect(self.text_changed)

        self.last_cursor_pos = None
        self.textChanged.connect(self.debouncer.start)

        self.default_header_fore: QColor = QColor(200, 200, 200, 255)
        self.default_header_back: QColor = QColor(20, 20, 20, 255)
        self.select_header_fore: QColor = QColor(255, 255, 200, 255)
        self.select_header_back: QColor = QColor(20, 20, 100, 255)

        self.section_element: str = ""
        self.section_selected: tuple[int, int, int] | None = None

        self.header_context_menu = HeaderContextMenu(self)

    @override
    def focusInEvent(self, e):
        self.update_cursor()
        super().focusInEvent(e)

    @override
    def focusOutEvent(self, e):
        self.last_cursor_pos = None
        super().focusOutEvent(e)

    @override
    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.update_cursor()

    @override
    def keyPressEvent(self, e):
        # Update cursor on keys that don't add characters
        if e.text() == '':
            self.update_cursor()
        super().keyPressEvent(e)
        
    @override
    def contextMenuEvent(self, e):
        if self.section_selected is not None:
            self.header_context_menu.exec(e.globalPos(), self.section_element)

    def update_cursor(self):
        self.last_cursor_pos = self.textCursor().position()
        if self.section_selected is not None:
            self.highlight_section(self.section_selected, (self.default_header_fore, self.default_header_back))
            self.section_selected = None
        for ele_id, offset in self.readable_offsets.items():
            h_len, off_s, off_e = offset
            try:
                if off_s - h_len < self.last_cursor_pos < off_e:
                    self.section_element = ele_id
                    if self.last_cursor_pos < off_s:
                        # print("header")
                        self.highlight_section(offset, (self.select_header_fore, self.select_header_back))
                        self.section_selected = offset
                        self.setReadOnly(True)
                        self.header_selected.emit(ele_id)
                    else:
                        # print("body")
                        self.setReadOnly(False)
                    break
                else:
                    self.section_element = ""
                    self.setReadOnly(True)
            except TypeError:
                print(ele_id)

    def seek_to_element(self, element_id):
        element = self.readable_offsets.get(element_id, None)
        if element is None: return

        h_len, start, end = element
        cursor = self.textCursor()
        if start == end:
            cursor.setPosition(start - h_len)
            self.highlight_section(element, (self.select_header_fore, self.select_header_back))
        else:
            cursor.setPosition(start + 1)
        self.setTextCursor(cursor)

        self.update_cursor()

    def render_script(self, script: CSCRTree):
        if script is None: return

        self.blockSignals(True)

        self.clear()
        readable_buffer: str = ""
        pos = 0

        for element_id, element in script.index_tree().items():
            header, body = CSCRTree.get_readable(element)
            if header is not None: head_len = len(header)
            else: head_len = 0
            if body is not None: body_len = len(body)
            else: body_len = 0

            if head_len > 0 or body_len > 0:
                start = head_len + pos
                self.readable_offsets[element_id] = (head_len, start, start + body_len)
                readable_buffer += f"{header}{body}"

            pos += head_len + body_len
        # Set text in editor
        self.setPlainText(readable_buffer)
        self.apply_formatting(self.readable_offsets)

        self.blockSignals(False)

    def highlight_section(self, offset: tuple[int, int, int], header_color: tuple[QColor, QColor], body_color: tuple[QColor, QColor] = (None, None)):
        cursor = QTextCursor(self.document())
        fmt_header = cursor.charFormat()
        fmt_header.setForeground(header_color[0])
        fmt_header.setBackground(header_color[1])

        header_len, start, end = offset
        cursor.setPosition(start - header_len)  # Position at the header
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, header_len)
        cursor.mergeCharFormat(fmt_header)

        if body_color == (None, None): return

        if body_color[0] is not None:
            fmt_header.setForeground(body_color[0])
        if body_color[1] is not None:
            fmt_header.setBackground(body_color[1])

        cursor.setPosition(start)  # Position at the header
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, end - start)
        cursor.mergeCharFormat(fmt_header)

    def apply_formatting(self, offset_map: dict[str, (int, int, int)]):
        """Applies visual formatting to section headers."""
        cursor = QTextCursor(self.document())
        fmt_header = QTextCharFormat()
        fmt_header.setForeground(QColor(200, 255, 200, 255))
        fmt_header.setBackground(QColor(0, 0, 0, 255))
        fmt_header.setFontWeight(600)

        for element_id, offset in offset_map.items():
            header_len, start, end = offset
            cursor.setPosition(start - header_len)  # Position at the header
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, header_len)
            cursor.mergeCharFormat(fmt_header)

    @pyqtSlot()
    def text_changed(self):
        cur_cursor_pos = self.textCursor().position()
        change_buffer = self.toPlainText()[self.last_cursor_pos:cur_cursor_pos]

        # print(f"Between {self.last_cursor_pos}:{cur_cursor_pos} - {change_buffer}\nChange length: {change_len}")

        changed_element = ""
        shift_elements: list[str] = []

        if self.last_cursor_pos is None: return

        for element_id, offsets in self.readable_offsets.items():
            h_len, off_s, off_e = offsets
            if off_s < self.last_cursor_pos < off_e:
                changed_element = element_id
                continue
            if not (changed_element == ""):
                shift_elements.append(element_id)

        if changed_element == "":
            return
        h_len, c_off_s, c_off_e = self.readable_offsets[changed_element]
        self.readable_offsets[changed_element] = (h_len, c_off_s, c_off_e + len(change_buffer))

        for element_id in shift_elements:
            h_len, off_s, off_e = self.readable_offsets[element_id]
            self.readable_offsets[element_id] = (h_len, off_s + len(change_buffer), off_e + len(change_buffer))

        self.last_cursor_pos = cur_cursor_pos
        """Emit the new text buffer."""
        self.script_updated.emit(changed_element, self.toPlainText()[c_off_s:c_off_e].strip('\n'))

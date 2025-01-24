# ~/projects/contenta/editor/editor_window.py
from xml.etree.ElementTree import Element

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox, QInputDialog
)

from PyQt6.QtCore import (
    Qt
)

from .cscr import CSCRTree
from .cscr_types import (
    ClipElement
)
from .text_area import TextArea
from .outline_pane import OutlinePane

from ui.menus import FileMenu


class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window properties
        self.setGeometry(100, 100, 1000, 600)

        # Create the main widget
        central_widget = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(central_widget)

        # Tree view for file structure
        self.tree_view = OutlinePane(self)
        self.tree_view.element_selected.connect(lambda element_id: self.text_editor.seek_to_element(element_id))
        central_widget.addWidget(self.tree_view)

        # Create a plain text editor
        self.text_editor = TextArea()
        self.text_editor.script_updated.connect(lambda ele_id, ele_text: self.cscr_file.set_property(ele_id, "content", ele_text))
        self.text_editor.header_selected.connect(lambda ele_id: print(ele_id))

        # Add the text editor to the layout
        central_widget.setSizes({1, 3})
        central_widget.addWidget(self.text_editor)

        # Add a menu bar
        menu_bar = FileMenu(self)
        menu_bar.get_action("New").triggered.connect(self.new_file)
        menu_bar.get_action("Load").triggered.connect(self.load_file)
        menu_bar.get_action("Save").triggered.connect(self.save_file)
        menu_bar.get_action("Change Title").triggered.connect(self.set_title_dialog)
        self.setMenuBar(menu_bar)
        self.update_title_bar()

        self.cscr_file: CSCRTree | None = None
        self.active_filename: str | None = None
        self.new_file()

        self.active_tag = None

    def update_title_bar(self, additional: str = ""):
        join_title = ""
        if additional != "":
            join_title = "".join(" - ")

        self.setWindowTitle(f"Contenta{join_title}{additional}")

    def new_file(self):
        """Handles creating a new .cscr file."""
        self.cscr_file = CSCRTree()
        self.active_filename = None
        self.tree_view.populate(self.cscr_file)

        self.update_title_bar(f"{self.cscr_file.get_tag_text("title")}")

        self.text_editor.render_script(self.cscr_file)

    def load_file(self):
        """Handles opening a .cscr file."""
        self.active_filename, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "CSCR Files (*.cscr);;All Files (*)"
        )
        if self.active_filename:
            try:
                self.cscr_file = CSCRTree.from_file(self.active_filename)
                self.tree_view.populate(self.cscr_file)
                self.text_editor.render_script(self.cscr_file)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")

    def save_file(self):
        """Handles saving the current content to a .cscr file."""
        if self.active_filename is None:
            self.active_filename, _ = QFileDialog.getSaveFileName(
                self, "Save File", "", "CSCR Files (*.cscr);;All Files (*)"
            )

        test_clip = { "title": "Testing Clip", "start": "0", "end": "10" }
        test_element = ClipElement.validate(test_clip)
        self.cscr_file.add_element(test_element)
        if self.active_filename:
            # Ensure the file has the .cscr extension
            if not self.active_filename.endswith(".cscr"):
                self.active_filename += ".cscr"
            try:
                self.cscr_file.to_file(self.active_filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")

    def set_title_dialog(self):
        new_title, ok = QInputDialog.getText(self, "New Script Title", "Enter a new title for this script...")
        if ok and len(new_title) > 0:
            for ele_id, element in self.cscr_file.index_tree().items():
                if element.tag == "title":
                    self.cscr_file.set_property(ele_id, "content", new_title)
                    self.update_title_bar(new_title)
                    return

    def select_element(self, element: Element):
        _, off, __ = self.cscr_file.get_element_offset(element)
        self.text_editor.move_to_pos(off)

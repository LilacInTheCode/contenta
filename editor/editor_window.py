# ~/projects/contenta/editor/editor_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox
)

from PyQt6.QtCore import (
    Qt
)

from .cscr import CSCRFile
from .text_area import TextArea
from .outline_pane import OutlinePane

from ui.menu_bar import FileMenu


class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window properties
        self.setWindowTitle("Contenta")
        self.setGeometry(100, 100, 1000, 600)

        # Create the main widget
        central_widget = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(central_widget)

        # Tree view for file structure
        self.tree_view = OutlinePane(self)
        self.tree_view.element_selected.connect(lambda element_id: print(element_id))
        central_widget.addWidget(self.tree_view)

        # Create a plain text editor
        self.text_editor = TextArea()
        self.text_editor.script_updated.connect(lambda ele_text: self.cscr_file.from_input(ele_text))

        # Add the text editor to the layout
        central_widget.setSizes({1, 3})
        central_widget.addWidget(self.text_editor)

        # Add a menu bar
        menu_bar = FileMenu(self)
        menu_bar.get_action("New").triggered.connect(self.new_file)
        menu_bar.get_action("Load").triggered.connect(self.load_file)
        menu_bar.get_action("Save").triggered.connect(self.save_file)
        self.setMenuBar(menu_bar)

        self.cscr_file: CSCRFile | None = None
        self.active_filename: str | None = None
        self.new_file()

        self.active_tag = None

    def new_file(self):
        """Handles creating a new .cscr file."""
        self.cscr_file = CSCRFile.from_empty()
        self.active_filename = None
        self.tree_view.populate(self.cscr_file)
        self.text_editor.render_script(self.cscr_file)

    def load_file(self):
        """Handles opening a .cscr file."""
        self.active_filename, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "CSCR Files (*.cscr);;All Files (*)"
        )
        if self.active_filename:
            try:
                self.cscr_file = CSCRFile.from_file(self.active_filename)
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

        if self.active_filename:
            # Ensure the file has the .cscr extension
            if not self.active_filename.endswith(".cscr"):
                self.active_filename += ".cscr"
            try:
                self.cscr_file.to_file(self.active_filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")


# ~/projects/contenta/ui/menu_bar.py

from PyQt6.QtWidgets import QMenuBar, QMenu, QWidget
from PyQt6.QtGui import QAction


class FileMenu(QMenuBar):
    def __init__(self, parent: QWidget):
        super().__init__(parent)


        self.menu_actions: dict[str, QAction] = {}

        file_menu: QMenu = self.addMenu("File")
        self.build_action(file_menu, "New")
        self.build_action(file_menu, None)
        self.build_action(file_menu, "Save")
        self.build_action(file_menu, "Load")
        self.build_action(file_menu, None)
        self.build_action(file_menu, "Exit")

        file_menu: QMenu = self.addMenu("Editor")
        self.build_action(file_menu, "Settings")

    def build_action(self, menu:QMenu, text: str | None) -> None:
        if text is None:
            menu.addSeparator()
        else:
            action = QAction(text)
            menu.addAction(action)
            self.menu_actions[text] = action

    def get_action(self, text: str) -> QAction | None:
        return self.menu_actions.get(text, None)

from PyQt6.QtWidgets import QTreeView
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtCore import Qt, pyqtSignal

from editor.cscr import CSCRFile


class OutlinePane(QTreeView):
    element_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Script Outline"])
        self.setModel(self.model)

        self.clicked.connect(self.on_tree_item_selected)

    def populate(self, script: CSCRFile):
        """Populates the tree view with the script structure."""
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Script Outline"])

        for element in script.root:

            if element.tag == "title": continue

            item_readable = element.attrib.get("readable", element.tag.capitalize())
            item = QStandardItem(item_readable)
            item.setData(element, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            self.model.appendRow(item)

    def on_tree_item_selected(self, index):
        self.element_selected.emit(self.model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole).get("id", "bad_id"))
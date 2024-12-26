from xml.etree.ElementTree import Element
from re import sub

from PyQt6.QtWidgets import QTreeView
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtCore import Qt, pyqtSignal

from editor.cscr import CSCRTree


class OutlinePane(QTreeView):
    element_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Script Outline"])
        self.setModel(self.model)

        self.clicked.connect(self.on_tree_item_selected)

    def populate(self, script: CSCRTree):
        """Populates the tree view with the script structure."""
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Script Outline"])

        for element_id, element in script.index_tree().items():

            if element.tag == "title": continue

            caption = CSCRTree.get_readable(element)[0]
            if caption is None: continue
            item = QStandardItem(sub(r"[\[\]]", "", caption))
            item.setData(element, Qt.ItemDataRole.UserRole)
            item.setData(element_id, Qt.ItemDataRole.UserRole + 1)
            item.setEditable(False)
            self._depth_populate(element, item)
            self.model.appendRow(item)

    def _depth_populate(self, element: Element, parent_obj: QStandardItem | QStandardItemModel):
        for child in element:
            child_item = QStandardItem(child.tag.capitalize())

            caption = CSCRTree.get_readable(element)[0]
            item = QStandardItem(sub(r"[\[\]]", "", caption))
            item.setData(element, Qt.ItemDataRole.UserRole)
            item.setData(element.get("id"), Qt.ItemDataRole.UserRole + 1)
            item.setEditable(False)

            parent_obj.appendRow(child_item)
            self._depth_populate(child, child_item)

    def on_tree_item_selected(self, index):
        self.element_selected.emit(self.model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole + 1))

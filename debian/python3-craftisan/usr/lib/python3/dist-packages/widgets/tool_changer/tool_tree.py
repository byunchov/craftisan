import typing as tp
from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QPixmap, QIcon
from PyQt5.QtWidgets import QTreeView, QWidget


class ToolTreeView(QTreeView):
    def __init__(self, parent: tp.Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.model_data: dict = None
        self.tree_model = QStandardItemModel()

        self.setModel(self.tree_model)
        self.setIconSize(QSize(36, 36))
        self.setHeaderHidden(True)

    @pyqtSlot(object)
    def loadTreeData(self, data: dict) -> None:
        self.model_data = data
        self.reloadTree()

    def createNode(self, displayName: str, nodeData, icon: str = None) -> QStandardItem:
        tree_item = QStandardItem(displayName)
        tree_item.setData(nodeData, Qt.UserRole)
        tree_item.setToolTip(displayName)
        tree_item.setIcon(QIcon(icon))
        tree_item.setEditable(False)

        return tree_item

    def createNode_old(self, displayName: str, nodeData, icon: bytes = None) -> QStandardItem:
        tree_item = QStandardItem(displayName)
        tree_item_icon_px = QPixmap()
        tree_item_icon_px.loadFromData(icon)
        tree_item.setData(nodeData, Qt.UserRole)
        tree_item.setIcon(QIcon(tree_item_icon_px))
        tree_item.setEditable(False)
        
        return tree_item

    def emptyResultNode(self):
        empty_item = QStandardItem("No tool data found")
        empty_item.setEditable(False)
        self.tree_model.appendRow(empty_item)

    @pyqtSlot()
    def reloadTree(self):
        self.tree_model.setRowCount(0)
        
        if not self.model_data:
            self.emptyResultNode()
            return        
        
        for category in self.model_data.values():
            cat_node = {"nodeType": category.get("nodeType", 'cat'), "id": category["id"]}
            category_item = self.createNode(category["displayName"], cat_node, category["icon"])
            self.tree_model.appendRow(category_item)

            if "subcategories" in category and isinstance(category["subcategories"], (tuple, list)):
                for subcategory in category["subcategories"]:
                    subcat_node = {"nodeType": subcategory.get("nodeType", 'subcat'), "id": subcategory["id"]}
                    subcategory_item = self.createNode(subcategory["displayName"], subcat_node, subcategory["icon"])
                    category_item.appendRow(subcategory_item)

                    if "tools" in subcategory and isinstance(subcategory["tools"], (tuple, list)):
                        for tool in subcategory["tools"]:
                            tool_node = {"nodeType": tool.get("nodeType", 'tool'), "id": tool["id"]}
                            tool_item = self.createNode(tool["displayName"], tool_node, tool["icon"])
                            subcategory_item.appendRow(tool_item)

        self.expandAll()

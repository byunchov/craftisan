import sys
from functools import partial
from PyQt5.QtCore import Qt, QSize, QModelIndex
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon
from PyQt5.QtWidgets import QApplication, QTreeView, QWidget, QMenu, QVBoxLayout, QMainWindow, QToolBar, QHBoxLayout
from craftisan.ui.windows.widgets import ToolEditWidget, ToolTreeView, ToolHelpWidget

import craftisan.craftisan_rc

class view(QWidget):
    def __init__(self, data):
        super(view, self).__init__()
        self.tree = QTreeView(self)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openMenu)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'Height', 'Weight'])
        self.tree.header().setDefaultSectionSize(180)
        self.tree.setModel(self.model)
        self.importData(data)
        self.tree.expandAll()

    def createNode(self, displayName: str, nodeData, icon: str = None) -> QStandardItem:
        tree_item = QStandardItem(displayName)
        tree_item.setData(nodeData, Qt.UserRole)
        tree_item.setIcon(QIcon(icon))
        tree_item.setEditable(False)

        return tree_item

    def importData(self, data:dict, root=None):
        self.model.setRowCount(0)
        
        if not data:
            return
        
        for category in data.values():
            cat_node = {"nodeType": category.get("nodeType", 'cat'), "id": category["id"]}
            category_item = self.createNode(category["displayName"], cat_node, category["icon"])
            self.model.appendRow(category_item)

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

        self.tree.expandAll()

    # Function to add right click menu to treeview item
    def openMenu(self, position):
            indexes = self.sender().selectedIndexes()
            mdlIdx = self.tree.indexAt(position)
            if not mdlIdx.isValid():
                return
            item = self.model.itemFromIndex(mdlIdx)

            item_data: dict = item.data(Qt.UserRole)
            node_type = item_data.get('nodeType', None)
            node_id = item_data.get('id', None)

            right_click_menu = QMenu()

            if node_type == "subcategory":
                act_add = right_click_menu.addAction(self.tr("Add Child Item"))
                act_add.triggered.connect(partial(self.TreeItem_Add, level, mdlIdx))                

            elif node_type == 'tool':
                insert_up = right_click_menu.addAction(self.tr("Insert Item Above"))
                insert_up.triggered.connect(partial(self.TreeItem_InsertUp, level, mdlIdx))

                insert_down = right_click_menu.addAction(self.tr("Insert Item Below"))
                insert_down.triggered.connect(partial(self.TreeItem_InsertDown, level, mdlIdx))

                act_del = right_click_menu.addAction(self.tr("Delete Item"))
                act_del.triggered.connect(partial(self.TreeItem_Delete, item))

            right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    def find_index_by_custom_data(self, custom_data):
        # Iterate through the model to find the index of the item with the specified custom data
        for row in range(self.model.rowCount()):
            for column in range(self.model.columnCount()):
                index = self.model.index(row, column)
                if index.data(Qt.UserRole) == custom_data:
                    return index
        return None

    # # Function to add child item to treeview item
    def TreeItem_Add(self, level, mdlIdx):
        temp_key = QStandardItem('xx')
        temp_value1 = QStandardItem('xx')
        temp_value2 = QStandardItem('xx')
        self.model.itemFromIndex(mdlIdx).appendRow([temp_key, temp_value1, temp_value2])
        self.tree.expand(mdlIdx)
        # self.tree.expandAll()

    # Function to Insert sibling item above to treeview item
    def TreeItem_InsertUp(self, level, mdlIdx: QModelIndex):
        level = level - 1
        current_row = self.model.itemFromIndex(mdlIdx).row()
        temp_key = QStandardItem('xx')
        temp_value1 = QStandardItem('xx')
        temp_value2 = QStandardItem('xx')
        self.model.itemFromIndex(mdlIdx).parent().insertRow(current_row, [temp_key, temp_value1, temp_value2])
        self.tree.expand(mdlIdx.parent())
        # self.tree.expandToDepth(1 + level)

    # Function to Insert sibling item above to treeview item
    def TreeItem_InsertDown(self, level, mdlIdx):
        level = level - 1
        temp_key = QStandardItem('xx')
        temp_value1 = QStandardItem('xx')
        temp_value2 = QStandardItem('xx')
        current_row = self.model.itemFromIndex(mdlIdx).row()
        self.model.itemFromIndex(mdlIdx).parent().insertRow(current_row + 1, [temp_key, temp_value1, temp_value2])
        # self.tree.expandToDepth(1 + level)

    # Function to Delete item
    def TreeItem_Delete(self, item):
        item.parent().removeRow(item.row())
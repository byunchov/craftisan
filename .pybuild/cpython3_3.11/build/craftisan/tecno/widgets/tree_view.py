import typing as tp
from functools import partial
from PyQt5.QtCore import Qt, QSize, pyqtSlot, pyqtSignal, QModelIndex, QItemSelection, QThreadPool
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon
from PyQt5.QtWidgets import QTreeView, QWidget, QMenu, QAction
from craftisan.tecno.widgets.edit_views.message_box import confirmAction
from craftisan.tool_db.model import Tool
from craftisan.utilities.worker import Worker
from craftisan.tool_db.queries import getToolTree
from craftisan.tecno.widgets.managers import DB_CHANGES

import linuxcnc

# STAT = linuxcnc.stat()
CMD = linuxcnc.command()


class ToolTreeView(QTreeView):
    changePreview = pyqtSignal(dict)
    insertTool = pyqtSignal(Tool)
    modifyTool = pyqtSignal(int)
    duplicateTool = pyqtSignal(int)

    def __init__(self, parent: tp.Optional[QWidget] = None, icon_size=36) -> None:
        super().__init__(parent)

        self.model_data: dict = None
        self.tree_model = QStandardItemModel()

        self._cmSwitch = {
            "category": self._categoryCM,
            "subcategory": self._subcategoryCM,
            "tool": self._toolCM
        }

        self.setModel(self.tree_model)
        self.selection_model = self.selectionModel()
        self.setIconSize(QSize(icon_size, icon_size))
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

        self._initActions()
        self._connectActions()
        self._connectSignals()
        self.fetchData()

    @pyqtSlot()
    def fetchData(self):
        worker = Worker(getToolTree)
        pool = QThreadPool.globalInstance()
        worker.signals.result.connect(self.loadTreeData)
        pool.start(worker)

    @pyqtSlot(object)
    def loadTreeData(self, data: dict) -> None:
        self.model_data = data
        self.reloadTree(expand_all=True)

    def createNode(self, displayName: str, nodeData, icon: str = None) -> QStandardItem:
        tree_item = QStandardItem(displayName)
        tree_item.setData(nodeData, Qt.UserRole)
        tree_item.setIcon(QIcon(icon))
        tree_item.setToolTip(displayName)
        tree_item.setEditable(False)
        return tree_item

    def emptyResultNode(self):
        empty_item = QStandardItem("No tool data found")
        empty_item.setEditable(False)
        empty_item.setToolTip(empty_item.text())
        self.tree_model.appendRow(empty_item)

    def _initActions(self):
        self.save_db_action = QAction(QIcon(':/images/dbms/save.png'), "&Save")
        self.reload_tree_action = QAction(QIcon(':/images/dbms/reload_tree.png'), "&Reload tree")
        self.reload_lcnc_action = QAction(QIcon(':/images/dbms/reload_lcnc.png'), "Reload &LCNC Table")

        self.add_tool_action = QAction(QIcon(':/images/dbms/add_button.png'), "&Add tool")
        self.modify_tool_action = QAction(QIcon(':/images/dbms/modify_button.png'), "&Modify tool")
        self.delete_tool_action = QAction(QIcon(':/images/dbms/delete_button.png'), "De&lete tool")
        self.duplicate_tool_action = QAction(QIcon(':/images/dbms/copy.png'), "&Duplicate")
       
        self.save_db_action.setShortcut("Ctrl+S")
        self.reload_tree_action.setShortcut("Ctrl+Shift+R")
        self.reload_lcnc_action.setShortcut("Alt+R")
        self.add_tool_action.setShortcut("Ctrl+N")
        self.modify_tool_action.setShortcut("Ctrl+M")
        self.delete_tool_action.setShortcut("Del")
        self.duplicate_tool_action.setShortcut("Ctrl+D")

        self.save_db_action.setEnabled(False)

    def _connectActions(self):
        self.save_db_action.triggered.connect(self.onSaveTool_Action)
        self.reload_tree_action.triggered.connect(self.onReloadTT_Action)
        self.reload_lcnc_action.triggered.connect(self.onReloadLCNCToolTable_Action)
        self.add_tool_action.triggered.connect(self.onAddTool_Action)
        self.modify_tool_action.triggered.connect(self.onModifyTool_Action)
        self.delete_tool_action.triggered.connect(self.onRemoveTool_Action)
        self.duplicate_tool_action.triggered.connect(self.onDuplicateTool_Action)

    def _connectSignals(self):
        # self.modifyTool.connect(print)
        # self.insertTool.connect(print)
        self.selection_model.selectionChanged.connect(self.onSelectionChanged)
        DB_CHANGES.listChanged.connect(self.save_db_action.setEnabled)

    def onSelectionChanged(self, selected: QItemSelection, deselected):
        try:
            index = selected.indexes()[0]

            if not index.isValid():
                return
            item = self.tree_model.itemFromIndex(index)
            item_data = item.data(Qt.UserRole)
            self.changePreview.emit(item_data)
        except IndexError:
            self.changePreview.emit({'nodeType': 'category', 'id': 1})
            return

    def openContextMenu(self, position):
        nodeIndex = self.indexAt(position)

        if not nodeIndex.isValid():
            return
        
        item = self.tree_model.itemFromIndex(nodeIndex)
        item_data: dict = item.data(Qt.UserRole)

        if not isinstance(item_data, dict):
            return
        
        node_type = item_data.get('nodeType', None)

        if node_type is None:
            return

        menu: QMenu = self._cmSwitch.get(node_type, self._categoryCM)(item)

        if menu is not None:
            menu.exec_(self.mapToGlobal(position))

    def _categoryCM(self, item: QStandardItem):
        itemIndex = item.index()
        contextMenu = QMenu(self)

        if self.isExpanded(itemIndex):
            collapse_branch_action = contextMenu.addAction("Collapse branch")
            collapse_branch_action.triggered.connect(partial(self.collapse, itemIndex))
        else:
            expand_branch_action = contextMenu.addAction("Expand branch")
            expand_branch_action.triggered.connect(partial(self.expand, itemIndex))
            
        contextMenu.addSeparator()

        contextMenu.addAction("Expand All").triggered.connect(self.expandAll)
        contextMenu.addAction("Collapse All").triggered.connect(self.collapseAll)

        return contextMenu

    def _subcategoryCM(self, item: QStandardItem):
        itemIndex = item.index()
        contextMenu = QMenu(self)
        contextMenu.addAction(self.add_tool_action)
        contextMenu.addSeparator()

        if self.isExpanded(itemIndex):
            collapse_branch_action = contextMenu.addAction("Collapse branch")
            collapse_branch_action.triggered.connect(partial(self.collapse, itemIndex))
        else:
            expand_branch_action = contextMenu.addAction("Expand branch")
            expand_branch_action.triggered.connect(partial(self.expand, itemIndex))

        return contextMenu

    def _toolCM(self, item: QStandardItem):
        contextMenu = QMenu(self)

        contextMenu.addAction(self.modify_tool_action)
        contextMenu.addAction(self.delete_tool_action)
        contextMenu.addSeparator()
        contextMenu.addAction(self.duplicate_tool_action)

        return contextMenu
    
    def _findIndexByData(self, nodeType: str, nodeId: int, parent=QModelIndex()) -> QModelIndex:
        for row in range(self.tree_model.rowCount(parent)):
            index = self.tree_model.index(row, 0, parent)
            nodeData = index.data(Qt.UserRole)
            
            if nodeData['nodeType'] == nodeType and nodeData['id'] == nodeId:
                return index

            # Recursively search in child items
            child_index = self._findIndexByData(nodeType, nodeId, index)
            if child_index.isValid():
                return child_index

        return QModelIndex()

    @pyqtSlot()
    def reloadTree(self, expand_all=False):
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

        if expand_all:
            self.expandAll()

    def onSaveTool_Action(self, *args):
        DB_CHANGES.commitChanges()
        # CMD.load_tool_table()

    def onReloadTT_Action(self, *args):
        if confirmAction(self, "Are you sure you want to <b>Reload</b> the table?\nThis action can't be undone!"):
            DB_CHANGES.discardChanges()
            self.fetchData()

    def onReloadLCNCToolTable_Action(self, *args):
        DB_CHANGES.commitChanges()
        CMD.load_tool_table()

    def onAddTool_Action(self, *args):
        try:
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return
            
            item = self.tree_model.itemFromIndex(index)
            item_data = item.data(Qt.UserRole)

            if item_data['nodeType'] not in ('subcategory', 'tool'):
                return
            
            if item_data['nodeType'] == 'tool':
                item_data = item.parent().data(Qt.UserRole)

            subId = int(item_data['id'])

            
            tool = Tool()
            tool.subCategoryId = subId
            # print(f"onAddTool_Action() -> {subId=}, {tool.subCategoryId=}")
            self.insertTool.emit(tool)
        except IndexError:
            return

    def onModifyTool_Action(self, *args):
        try:
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return
            
            item = self.tree_model.itemFromIndex(index)
            item_data = item.data(Qt.UserRole)

            if item_data['nodeType'] != 'tool':
                return
            
            self.modifyTool.emit(item_data.get('id', 0))
        except IndexError:
            return

    def onDuplicateTool_Action(self, *args):
        try:
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return
            
            item = self.tree_model.itemFromIndex(index)
            item_data = item.data(Qt.UserRole)

            if item_data['nodeType'] != 'tool':
                return
            
            self.duplicateTool.emit(item_data.get('id', 0))
        except IndexError:
            return

    @pyqtSlot()
    def onRemoveTool_Action(self, *args):
        # index = self._findIndexByData('tool', tool.id)
        try:
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return
            
            item = self.tree_model.itemFromIndex(index)
            item_data = item.data(Qt.UserRole)

            if item_data['nodeType'] != 'tool':
                return
            
            tool_id = item_data['id']
            
            if confirmAction(self, f"Are you sure you want to delete T{tool_id}"):
                item.parent().removeRow(item.row())
                DB_CHANGES.removeItem(tool_id)
        except IndexError:
            return
    
    @pyqtSlot(Tool)
    def addTool(self, tool: Tool):
        index = self._findIndexByData('subcategory', tool.subCategoryId)

        if not index.isValid():
            return
        
        toolIndex = self._findIndexByData('tool', tool.id, parent=index)
        
        if toolIndex.isValid():
            return
        
        node = self.createNode(str(tool), {"nodeType": 'tool', "id": tool.id}, tool.icon)
        
        self.tree_model.itemFromIndex(index).appendRow(node)
        self.expand(index)

        # DB_CHANGES.saveItem(tool)

    @pyqtSlot(Tool)
    def updateTool(self, tool: Tool):
        index = self._findIndexByData('tool', tool.id)

        if not index.isValid():
            return
        
        item = self.tree_model.itemFromIndex(index)
        description = str(tool)
        item.setData({"nodeType": 'tool', "id": tool.id})
        item.setIcon(QIcon(tool.icon))
        item.setText(description)
        item.setToolTip(description)

        # DB_CHANGES.saveItem(tool)


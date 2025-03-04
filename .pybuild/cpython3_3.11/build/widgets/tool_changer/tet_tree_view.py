import sys
from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QPushButton, QVBoxLayout, QWidget

class CustomModel(QAbstractItemModel):
    def __init__(self, root_item, parent=None):
        super().__init__(parent)
        self.root_item = root_item
        self.expanded_items = []

    def rowCount(self, parent_index):
        if parent_index.isValid():
            return parent_index.internalPointer().child_count()
        return self.root_item.child_count()

    def columnCount(self, parent_index):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.data(index.column())

        return None

    def index(self, row, column, parent_index):
        if not self.hasIndex(row, column, parent_index):
            return QModelIndex()

        if not parent_index.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent_index.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return super().flags(index)

    def expandItem(self, index):
        item = index.internalPointer()
        if item not in self.expanded_items:
            self.expanded_items.append(item)

    def isItemExpanded(self, index):
        return index.internalPointer() in self.expanded_items

    def updateData(self, root_item):
        self.beginResetModel()
        self.root_item = root_item
        self.endResetModel()

class TreeItem:
    def __init__(self, data, parent=None):
        self.parent_item = parent
        self.item_data = data
        self.child_items = []

    def appendChild(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def column_count(self):
        return len(self.item_data)

    def data(self, column):
        if 0 <= column < len(self.item_data):
            return self.item_data[column]
        return None

    def parent(self):
        return self.parent_item

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

def createSampleData():
    root_item = TreeItem(["Root"])
    for i in range(1, 6):
        child_item = TreeItem([f"Child {i}"], parent=root_item)
        root_item.appendChild(child_item)
        for j in range(4):
            sub_child = TreeItem([f"Sub-Child {i}"], parent=child_item)
            child_item.appendChild(sub_child)
            for k in range(8):
                sub2 = TreeItem([f"Last Child {i}"], parent=sub_child)
                sub_child.appendChild(sub2)
    return root_item

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tree_view = QTreeView()
        self.root_item = createSampleData()
        self.model = CustomModel(self.root_item)
        self.tree_view.setModel(self.model)

        self.expand_button = QPushButton("Expand")
        self.expand_button.clicked.connect(self.expandSelectedItems)

        layout = QVBoxLayout()
        layout.addWidget(self.tree_view)
        layout.addWidget(self.expand_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def expandSelectedItems(self):
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        for index in selected_indexes:
            self.model.expandItem(index)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

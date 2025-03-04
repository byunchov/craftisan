import sys
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QTableWidgetItem, QSizePolicy, QCheckBox, QStyledItemDelegate
from PyQt5.QtGui import QCursor, QKeyEvent

class CheckBoxDelegate1(QStyledItemDelegate):
    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self._checked = checked

    def createEditor(self, parent, option, index):
        checkbox = QCheckBox(parent)
        checkbox.setTristate(False)
        checkbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        checkbox.setChecked(self._checked)
        option.displayAlignment = Qt.AlignCenter
        return checkbox

    def setEditorData(self, editor:QCheckBox, index):
        value = index.data(Qt.EditRole)
        editor.setChecked(bool(value))
        # if value is not None:
        #     editor.setChecked(bool(value))

    def setModelData(self, editor: QCheckBox, model, index):
        model.setData(index, editor.isChecked(), Qt.EditRole)

    def updateEditorGeometry(self, editor: QCheckBox, option, index):
        editor.setGeometry(option.rect)

class CustomTableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self.data = data
        self.headers = headers

    def rowCount(self, parent=QModelIndex()):
        return len(self.data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.data[0])

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]
        return None

class CustomTableView(QTableView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.setMouseTracking(True)
        self.start_index = None
        self.copy_mode = False

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifier = event.modifiers()
        current_index = self.currentIndex()
        selected_indexes = self.selectedIndexes()
        row_count =  self.model().rowCount()
        if key == Qt.Key_Down and (modifier & Qt.ControlModifier):
            if current_index.isValid():
                first_index = selected_indexes[0]
                next_row = current_index.row() + 1
                if first_index.row() < next_row < row_count:
                    self.selectColumn(first_index.column())
                    self.selectRow(next_row)
                # if current_index.row() < self.start_index.row():
                #     self.selectRow(current_index.row(), self.start_index.row() + 1)
                # else:
                #     self.selectRow(self.start_index.row(), current_index.row() + 1)
                self.update()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    data = [[f"Row {i}, Col {j}" for j in range(10)] for i in range(10)]
    headers = [f"Header {i}" for i in range(10)]
    model = CustomTableModel(data, headers)
    table = CustomTableView(model)

    window = QMainWindow()
    window.setCentralWidget(table)
    window.setGeometry(100, 100, 800, 400)
    window.show()

    sys.exit(app.exec_())

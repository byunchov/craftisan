import sys, os
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtCore import Qt, QAbstractTableModel, QEvent, QModelIndex
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableView, QItemDelegate, QFileDialog, 
QStyledItemDelegate, QPushButton, QComboBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCompleter, QHeaderView)


class CheckBoxDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox cell of the column to which it's applied.
    """
    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        """
        Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def paint(self, painter, option, index):
        """
        Paint a checkbox without the label.
        """
        self.drawCheck(painter, option, option.rect, Qt.Checked if bool(index.data()) else Qt.Unchecked)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton and this cell is editable. Otherwise do nothing.
        '''
        if not int(index.flags() & Qt.ItemIsEditable) > 0:
            return False
        
        event_type = event.type()

        is_mouse_click = isinstance(event, QMouseEvent) and \
            (event_type == event.MouseButtonRelease and event.button() == Qt.LeftButton)
        is_key_press = isinstance(event, QKeyEvent) and \
            (event_type == event.KeyPress and event.key() == Qt.Key_Space)

        if is_mouse_click or is_key_press:
            self.setModelData(None, model, index)
            return True

        return False

    def setModelData (self, editor, model, index):
        '''
        The user wanted to change the old state in the opposite.
        '''
        model.setData(index, not bool(index.data()), Qt.EditRole)

class FileChoserDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        file_dialog = QFileDialog(parent)
        file_dialog.setMinimumSize(900, 600)
        file_dialog.setNameFilters(["All files (*.*)", "PyG/NGC Files (*.pyg, *.ngc)"])
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setOption(QFileDialog.Option.ReadOnly, True)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        return file_dialog
        # return self.fdialog

    def setEditorData(self, editor: QFileDialog, index):
        file_path = index.data(Qt.EditRole)
        editor.selectFile(file_path)

    def setModelData(self, editor: QFileDialog, model, index):
        selected_files = editor.selectedFiles()
        if len(selected_files) == 1:
            file_path = selected_files[0]
            file_name = os.path.basename(file_path)
            model.setData(index, file_path, Qt.EditRole)
            model.setData(index, file_name, Qt.DisplayRole)

class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items: dict[int, str] = items

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        for key, value in self.items.items():
            combo.addItem(value, key)
        combo.setCurrentIndex(0)
        return combo

    def setEditorData(self, editor: QComboBox, index):
        value = index.data(Qt.EditRole)
        if value is not None:
            editor.setCurrentText(self.items[int(value)])

    def setModelData(self, editor: QComboBox, model, index):
        user_data = editor.currentData(Qt.UserRole)
        model.setData(index, user_data, Qt.EditRole)
        model.setData(index, editor.currentText(), Qt.DisplayRole)

class LineEditDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)
        self._text: str = text or ''

    def createEditor(self, parent, option, index):
        row, column = index.row(), index.column()
        row_count = index.model().rowCount()

        completions = []
        if column in (7, 8, 9):
            completions = tuple(f'{d}({i})' for d in 'lhs' for i in range(row_count) if i != row)
        elif column in (10, 11, 12):
            completions = tuple(f'of{o}({i})' for o in 'xyz' for i in range(row_count) if i != row)

        print(f'{completions=}')

        line_edit = QLineEdit(parent)
        completer = QCompleter(completions)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        line_edit.setText(self._text)
        line_edit.setCompleter(completer)
        return line_edit

    def setEditorData(self, editor: QLineEdit, index):
        value = index.data(Qt.EditRole)
        editor.setText(str(value))

    def setModelData(self, editor: QLineEdit, model, index):        
        old_data = index.data(Qt.EditRole)
        new_data = editor.text()
        # if isinstance(old_data, int):
        #     new_data = int(new_data)
        # elif isinstance(old_data, float):
        #     new_data = float(new_data)

        model.setData(index, new_data, Qt.EditRole)

class CustomTableModel(QAbstractTableModel):
    default_row = (False, '', None, 1, 0, False, False, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def __init__(self, data, headers):
        super().__init__()
        self.data = data
        self.headers = headers
        self.display_data = data or [list(self.default_row)]
        self.edit_data = data or [list(self.default_row)]
        self.cut_copy_data = []

        self.checkbox_delegate = CheckBoxDelegate()
        self.file_delegate = FileChoserDelegate()
        self.text_delegate = LineEditDelegate()
        self.area_delegate = ComboBoxDelegate({i: f'Area {i:2d}' for i in range(1, 10)})

        self.__eval_locals = {
            'l': self.wpLenghtFromRow,
            'h': self.wpHeightromRow,
            's': self.wpThicknessFromRow,
            'ofx': self.wpOffsetXFromRow,
            'ofy': self.wpOffsetYFromRow,
            'ofz': self.wpOffsetZFromRow,
        }

    def rowCount(self, *args):
        return len(self.display_data)

    def columnCount(self, *args):
        return len(self.display_data[0])

    def data(self, index, role=Qt.DisplayRole):
        row, column = index.row(), index.column()

        if role == Qt.DisplayRole:

            if column in range(7, 13):
                return self.evalExpression(self.edit_data[row][column])
            
            return self.display_data[row][column]
        
        if role == Qt.EditRole:
            return self.edit_data[row][column]
        
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.DisplayRole:
            row, column = index.row(), index.column()
            self.display_data[row][column] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole])
            return True
        

        if role == Qt.EditRole:
            row, column = index.row(), index.column()
            self.edit_data[row][column] = value
            if column in range(7, 13):
                self.display_data[row][column] = self.evalExpression(value)
            else:
                self.display_data[row][column] = value

            self.dataChanged.emit(index, index, [Qt.EditRole])
            return True
        
        return False

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return super().headerData(section, orientation, role)
    
    def insertRow(self, position, parent=None):
        if parent is None:
            parent = QModelIndex()
        
        self.beginInsertRows(parent, position, position)
        self.display_data.insert(position, list(self.default_row))
        self.edit_data.insert(position, list(self.default_row))
        self.endInsertRows()
        
    def insertRows(self, position, rows, parent=None):
        if parent is None:
            parent = QModelIndex()
        
        self.beginInsertRows(parent, position, position + rows - 1)
        for _ in range(rows):
            self.data.insert(position, [""] * self.columnCount())
        self.endInsertRows()

    def removeRows(self, position, rows, parent=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        del self.data[position:position + rows]
        self.endRemoveRows()

    def cut(self, selected_rows):
        self.cut_copy_data = [self.data[row.row()] for row in selected_rows]
        self.removeRows(selected_rows[0].row(), len(selected_rows))

    def copy(self, selected_rows):
        self.cut_copy_data = [self.data[row.row()] for row in selected_rows]


    def evalExpression(self, value: str):
        try:
            result = eval(str(value), None, self.__eval_locals)
            if isinstance(result, (int, float, bool)):
                return result
            else:
                return self.evalExpression(result)
        except (SyntaxError, NameError, TypeError, ValueError):
            return None
    
    def wpLenghtFromRow(self, row: int):
        return self.index(row, 7).data(Qt.EditRole)
    
    def wpHeightromRow(self, row: int):
        return self.index(row, 8).data(Qt.EditRole)
    
    def wpThicknessFromRow(self, row: int):
        return self.index(row, 9).data(Qt.EditRole)
    
    def wpOffsetXFromRow(self, row: int):
        return self.index(row, 10).data(Qt.EditRole)
    
    def wpOffsetYFromRow(self, row: int):
        return self.index(row, 11).data(Qt.EditRole)
    
    def wpOffsetZFromRow(self, row: int):
        return self.index(row, 12).data(Qt.EditRole)

class CustomTableView(QTableView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        # self.setMouseTracking(True)
        self.horizontal_header = self.horizontalHeader()

        self.check_delegate = CheckBoxDelegate()
        self.file_delegate = FileChoserDelegate()
        self.text_delegate = LineEditDelegate()
        self.area_delegate = ComboBoxDelegate({i: f'Area {i:2d}' for i in range(1, 10)})
        self.setItemDelegateForColumn(0, self.check_delegate)
        self.setItemDelegateForColumn(5, self.check_delegate)
        self.setItemDelegateForColumn(6, self.check_delegate)
        self.setItemDelegateForColumn(1, self.file_delegate)
        self.setItemDelegateForColumn(2, self.area_delegate)
        self.setItemDelegateForColumn(7, self.text_delegate)
        self.setItemDelegateForColumn(8, self.text_delegate)
        self.setItemDelegateForColumn(9, self.text_delegate)
        self.setItemDelegateForColumn(10, self.text_delegate)
        self.setItemDelegateForColumn(11, self.text_delegate)
        self.setItemDelegateForColumn(12, self.text_delegate)

        self.horizontal_header.setSizeAdjustPolicy(QHeaderView.AdjustToContents)
        self.horizontal_header.resizeSections(QHeaderView.ResizeToContents)
        self.horizontal_header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.selection_model = self.selectionModel()
        self.selection_model.currentChanged.connect(self.onCurrentChange)

    def onCurrentChange(self, selected: QModelIndex, prev: QModelIndex):
        if selected:
            print(f"{selected.data(Qt.EditRole)=}, {selected.data(Qt.DisplayRole)=}")

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()
        ctrl_modifier = modifiers & Qt.ControlModifier
        if key in (Qt.Key_Up, Qt.Key_Down) and ctrl_modifier :
            selected = self.selectedIndexes() if key == Qt.Key_Down else self.selectedIndexes()[::-1]
            model = self.model()
            if len(selected) > 1:
                cell_display_data = selected[0].data(Qt.DisplayRole)
                cell_edit_data = selected[0].data(Qt.EditRole)
                for cell in selected:
                    model.setData(cell, cell_edit_data, Qt.EditRole)
                    model.setData(cell, cell_display_data, Qt.DisplayRole)
        # elif key == Qt.Key_Minus and ctrl_modifier:
        #     selected = self.selectedIndexes()
        #     if len(selected) > 0:
        #         model = selected[0].model()
        #         current_row = selected[0].row()
        #         model.insertRow(current_row + 1)
        # elif key == Qt.Key_Plus and ctrl_modifier:
        #     selected = self.selectedIndexes()
        #     if len(selected) > 0:
        #         model = selected[0].model()
        #         current_row = selected[0].row()
        #         model.insertRow(current_row - 1 if current_row > 0 else 0)
        elif key in (Qt.Key_Minus, Qt.Key_Plus) and ctrl_modifier:
            selected = self.selectedIndexes()
            if len(selected) > 0:
                model = selected[0].model()
                current_row = selected[0].row()
                if key == Qt.Key_Minus:
                    new_row = current_row - 1 if current_row > 0 else 0
                else:
                    new_row = current_row + 1
                model.insertRow(new_row)

        super().keyPressEvent(event)

class TableExample(QMainWindow):
    headers = ('Exec.', 'File', 'Area', 'Repetitions', 'Executed', 'Merge', 'Group', 'L', 'H', 'S',
                   'Offset X', 'Offset Y', 'Offset Z')

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Table Example')
        self.setGeometry(100, 100, 1200, 800)

        widget = QWidget()
        vlay = QVBoxLayout()
        hl = QHBoxLayout()

        # data = [list(self.default_row)]

        self.table_model = CustomTableModel(None, self.headers)
        self.table_widget = CustomTableView(self.table_model)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_model.dataChanged.connect(self.onDataChange)

        self.add_row_button = QPushButton("Add Row")        

        hl.addWidget(self.add_row_button)

        vlay.addWidget(self.table_widget)
        vlay.addLayout(hl)
        widget.setLayout(vlay)
        self.setCentralWidget(widget)

        self.add_row_button.clicked.connect(self.onAddRowClicked)

    def onDataChange(self, top: QModelIndex, bottom: QModelIndex, roles: list[Qt.ItemDataRole]):
        print(f"top=[{top.row()}, {top.column()}], bottom=[{bottom.row()}, {bottom.column()}], {roles=}")
        # self.table_widget.resizeColumnsToContents()

    def onAddRowClicked(self):
        self.table_model.insertRow(self.table_model.rowCount(None))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TableExample()
    window.show()
    sys.exit(app.exec_())

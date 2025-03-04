import sys, os
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtCore import Qt, QAbstractTableModel, QEvent, QModelIndex
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableView, QItemDelegate, QFileDialog, 
QStyledItemDelegate, QPushButton, QComboBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCompleter, QHeaderView)
from enum import Enum
from gcode_paser import parse_gcode


class FillDirection(Enum):
    FillDown = 1
    FillUp = 2


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
        file_dialog.setMinimumSize(700, 500)
        file_dialog.setNameFilters(["All files (*.*)", "PyG/NGC Files (*.pyg, *.ngc)"])
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setOption(QFileDialog.ReadOnly, True)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, False)
        return file_dialog
        # return self.fdialog

    def setEditorData(self, editor: QFileDialog, index):
        file_path = index.data(Qt.EditRole)
        editor.selectFile(file_path)

    def setModelData(self, editor: QFileDialog, model, index):
        selected_files = editor.selectedFiles()
        if len(selected_files) == 1:
            file_path = selected_files[0]
            model.setData(index, file_path, Qt.EditRole)

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

        # print(f'{completions=}')

        line_edit = QLineEdit(parent)
        completer = QCompleter(completions, line_edit)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        # completer.setModel()
        # line_edit.setText(self._text)
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

    default_row = (True, '', 2, 1, 0, False, False, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    area_values = {i: f'Area {i:2d}' for i in range(1, 10)}

    def __init__(self, data, headers):
        super().__init__()
        self.headers = headers
        self.display_data = data or [list(self.default_row)]
        self.cut_copy_data = []

        self.checkbox_delegate = CheckBoxDelegate()
        self.file_delegate = FileChoserDelegate()
        self.text_delegate = LineEditDelegate()
        self.area_delegate = ComboBoxDelegate(self.area_values)

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
        try:
            return len(self.display_data[0])
        except:
            return len(self.default_row)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row, column = index.row(), index.column()
            self.display_data[row][column] = value
            self.dataChanged.emit(index, index, [Qt.EditRole])
            return True        
        return False

    def data(self, index, role=Qt.DisplayRole):
        row, column = index.row(), index.column()

        if role == Qt.DisplayRole:
            if column == 1:
                file_path = self.display_data[row][column]
                file_name = os.path.basename(file_path) if os.path.isfile(file_path) else ''
                return file_name
            elif column == 2:
                area_code = self.display_data[row][column]
                return self.area_values[area_code] if area_code is not None else None
            elif column in range(7, 13):
                cell_value = self.evalExpression(self.display_data[row][column])
                if isinstance(cell_value, str):
                    cell_value = float(cell_value)
                return f"{cell_value:.3f}"
            return self.display_data[row][column]
        
        if role == Qt.EditRole:
            return self.display_data[row][column]
        
        return None
    
    def flags(self, index):
        flags = super().flags(index)
        row, column = index.row(), index.column()
        no_file_selected = self.display_data[row][1] == '' and column != 1
        merge_not_enabled = not self.display_data[row][5] and column == 6

        flags |= Qt.ItemIsEditable
        if no_file_selected or merge_not_enabled:
            flags &= ~Qt.ItemIsEditable  # Remove the Qt.ItemIsEditable flag

        return flags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return super().headerData(section, orientation, role)
    
    def insertRow(self, position, parent=None, above=False, at_end=True):
        if parent is None:
            parent = QModelIndex()

        if self.display_data is None:
            self.display_data = list()
        
        row_count = len(self.display_data)
        position = row_count if at_end else position

        if not above:
            position += 1
        
        self.beginInsertRows(parent, position, position)
        self.display_data.insert(position, list(self.default_row))
        self.endInsertRows()
        
    def insertRows(self, position, rows, parent=None):
        if parent is None:
            parent = QModelIndex()

        if self.display_data is None or len(self.display_data) < 1:
            self.display_data = list()
            position = 0

        if isinstance(rows, (list, tuple)):
            row_count = len(rows)
            if row_count < 1:
                return

            self.beginInsertRows(parent, position, position + row_count - 1)
            for i, row_data in enumerate(rows):
                self.display_data.insert(position + i, list(row_data))
            self.endInsertRows()
        
        if isinstance(rows, int):
            self.beginInsertRows(parent, position, position + rows - 1)
            for i in range(rows):
                self.display_data.insert(position + i, list(self.default_row))
            self.endInsertRows()

    def removeRow(self, position, parent=None):
        if self.display_data is None or len(self.display_data) < 1:
            return

        self.beginRemoveRows(QModelIndex(), position, position)
        self.display_data.pop(position)
        self.endRemoveRows()

        if len(self.display_data) == 0:
            self.insertRow(0)

    def removeRows(self, position, rows, parent=None):
        if self.display_data is None or len(self.display_data) < 1:
            return
        
        if rows < 1:
            return

        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        del self.display_data[position:position + rows]
        self.endRemoveRows()

        if len(self.display_data) == 0:
            self.insertRow(0)
    
    def deleteRows(self, selected_indices):
        if self.display_data is None or len(self.display_data) < 1:
            return
        
        if not isinstance(selected_indices, (list, tuple)):
            return
        
        if len(selected_indices) < 1:
            return
        
        if isinstance(selected_indices[0], QModelIndex):
            row_indices = [row.row() for row in selected_indices]
        elif isinstance(selected_indices[0], int):
            row_indices = selected_indices.copy()
        
        row_indices.sort(reverse=True)

        self.beginRemoveRows(QModelIndex(), row_indices[-1], row_indices[0])
        try:
            for index in row_indices:
                self.display_data.pop(index)
        except IndexError:
            pass
        self.endRemoveRows()

        print(self.display_data)

        if len(self.display_data) == 0:
            self.insertRow(0)

    def cutRows(self, selected_indices):
        if self.display_data is None or len(self.display_data) < 1:
            return
        
        if not isinstance(selected_indices, (list, tuple)):
            return
        
        if len(selected_indices) < 1:
            return
        
        if isinstance(selected_indices[0], QModelIndex):
            row_indices = [row.row() for row in selected_indices]
        elif isinstance(selected_indices[0], int):
            row_indices = selected_indices.copy()
        
        cut_data = list()
        
        parent = QModelIndex()
        for index in sorted(row_indices, reverse=True):
            self.beginRemoveRows(parent, index, index)
            cut_data.append(self.display_data.pop(index))
            self.endRemoveRows()
        
        self.cut_copy_data = tuple(reversed(cut_data))

        if len(self.display_data) == 0:
            self.insertRow(0)

    def copyRows(self, selected_indices):
        if self.display_data is None or len(self.display_data) < 1:
            return
        if not isinstance(selected_indices, (list, tuple)):
            return
        
        if len(selected_indices) < 1:
            return
        
        if isinstance(selected_indices[0], QModelIndex):
            row_indices = [row.row() for row in selected_indices]
        elif isinstance(selected_indices[0], int):
            row_indices = selected_indices.copy()
        
        self.cut_copy_data = tuple(self.display_data[row] for row in row_indices)

    def pasteRows(self, selected_indices):
        if self.cut_copy_data is None or len(self.cut_copy_data) < 1:
            return
    
        if not isinstance(selected_indices, (list, tuple)) or len(selected_indices) < 1:
            return
        
        position = selected_indices[0]        
        
        if isinstance(position, QModelIndex):
            row_index = position.row() + 1
        elif isinstance(position, int):
            row_index = position + 1
        
        self.insertRows(row_index, self.cut_copy_data)

    def fillRange(self, selected_indices: list, direction = FillDirection.FillDown):
        if self.display_data is None or len(self.display_data) < 1:
            return
        
        if not isinstance(selected_indices, (list, tuple)):
            return
        
        if len(selected_indices) < 1:
            return
        
        if not isinstance(selected_indices[0], QModelIndex):
            return
        
        if direction == FillDirection.FillUp:
            selected_indices = selected_indices[::-1]

        cell_edit_data = selected_indices[0].data(Qt.EditRole)
        for cell in selected_indices:
            self.setData(cell, cell_edit_data)

    def evalExpression(self, value: str):
        try:
            result = eval(str(value), {}, self.__eval_locals)
            if isinstance(result, (int, float, bool)):
                return float(result)
            return self.evalExpression(result)
        except (SyntaxError, NameError, TypeError, ValueError):
            return 0.0
    
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
    FILE_EXT = ('.ngc', '.nc')

    def __init__(self, model=None):
        super().__init__()
        self.data_model = model or CustomTableModel()
        self.setModel(self.data_model)
        # self.setMouseTracking(True)
        self.horizontal_header = self.horizontalHeader()
        self.current_row = -1

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
        if not selected:
            return
        
        row = selected.row()
        print(f"onCurrentChange() {row=}")
        if row != self.current_row:
            self.current_row = row

            file_path: str = selected.model().index(row, 1).data(Qt.EditRole)
            print(f"{file_path=}")

            if file_path != '' and file_path.endswith(self.FILE_EXT):
                result = parse_gcode(file_path)
                print(result['dim'])
                print(result['offsets'])
        
        # print(f"{selected.data(Qt.EditRole)=}, {selected.data(Qt.DisplayRole)=}")

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()
        ctrl_modifier = modifiers & Qt.ControlModifier
        selected = self.selectedIndexes()

        if key in (Qt.Key_Up, Qt.Key_Down) and ctrl_modifier:
            direction = FillDirection.FillDown if key == Qt.Key_Down else FillDirection.FillUp
            self.data_model.fillRange(selected, direction)            
        elif key in (Qt.Key_Minus, Qt.Key_Plus) and ctrl_modifier:
            if len(selected) > 0:
                self.data_model.insertRow(selected[0].row(), at_end=False, above=(key == Qt.Key_Minus))
        elif key == Qt.Key_X and ctrl_modifier:
            self.data_model.cutRows(selected)
        elif key == Qt.Key_C and ctrl_modifier:
            self.data_model.copyRows(selected)
        elif key == Qt.Key_V and ctrl_modifier:
            self.data_model.pasteRows(selected)
        elif key == Qt.Key_Delete:
            self.data_model.deleteRows(selected)

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
        # self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_model.dataChanged.connect(self.onDataChange)

        self.add_row_btn = QPushButton("Add Row")
        self.cut_row_btn = QPushButton("Cut Row")
        self.copy_row_btn = QPushButton("Copy Row")
        self.paste_row_btn = QPushButton("Paste Row")

        hl.addWidget(self.add_row_btn)
        hl.addWidget(self.cut_row_btn)
        hl.addWidget(self.copy_row_btn)
        hl.addWidget(self.paste_row_btn)

        vlay.addWidget(self.table_widget)
        vlay.addLayout(hl)
        widget.setLayout(vlay)
        self.setCentralWidget(widget)

        self.add_row_btn.clicked.connect(self.onAddRowClicked)
        self.cut_row_btn.clicked.connect(self.onCutRowClicked)
        self.copy_row_btn.clicked.connect(self.onCopyRowClicked)
        self.paste_row_btn.clicked.connect(self.onPasteRowClicked)

    def onDataChange(self, top: QModelIndex, bottom: QModelIndex, roles: list[Qt.ItemDataRole]):
        pass
        # print(f"top=[{top.row()}, {top.column()}], bottom=[{bottom.row()}, {bottom.column()}], {roles=}")
        # self.table_widget.resizeColumnsToContents()

    def onAddRowClicked(self):
        self.table_model.insertRow(self.table_model.rowCount(None))
    
    def onCutRowClicked(self):
        self.table_model.cutRows(self.table_widget.selectedIndexes())

    def onCopyRowClicked(self):
        self.table_model.copyRows(self.table_widget.selectedIndexes())
    
    def onPasteRowClicked(self):
        selectedIndexes = self.table_widget.selectedIndexes()
        if len(selectedIndexes) < 1:
            return        
        self.table_model.pasteRows(selectedIndexes[0])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TableExample()
    window.show()
    sys.exit(app.exec_())

import os
from typing import Union
from PyQt5.QtWidgets import QHeaderView, QTableView, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize, QAbstractTableModel, pyqtSignal, pyqtSlot, QTimer
from qtpy.QtCore import Property
import linuxcnc as cnc

from qtpyvcp.actions.machine_actions import issue_mdi

from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.plugins import getPlugin
from qtpyvcp.widgets.dialogs import getDialog
# from craftisan.ui.dialogs.tool_db.select_tool import SelectToolDialog


LOG = getLogger(__name__)

IN_DESIGNER = os.getenv('DESIGNER', False)

COLUMN_HEADERS = ('#', 'Description', 'D', 'Lenght')

class TableModel(QAbstractTableModel):
    current_tool_bg = QColor('#285c25')
    vacant_pocket_bg = QColor('#2c662d')
    occupied_pocket_bg = QColor('#965a2f')
    default_tool_icon = None
    empty_row = (None, 'Add tool...', None, None, None)

    model_changed = pyqtSignal()
    unsavedChanges = pyqtSignal(bool)
    enableTable = pyqtSignal(bool)
    enableSpindleLoad = pyqtSignal(bool)

    def __init__(self, tc_id: int, data: list=None, row_headers: list=None, column_headers: list=None):
        super(TableModel, self).__init__()
        self.changer_id = tc_id
        self.model_data = data or []
        self.row_headers = row_headers or []
        self.column_headers = column_headers or COLUMN_HEADERS

        self.unsaved_changes: bool = False

        self.status = getPlugin('status')
        self.stat = self.status.stat
        self.tt = getPlugin('tooltable')

        self.status.tool_in_spindle.notify(self.refreshModel)
        self.status.interp_state.notify(self._emitTableEnableSignal)
        self.status.task_state.notify(self._emitTableEnableSignal)
        self.status.task_mode.notify(self._emitTableEnableSignal)
        self.tt.toolchanger_changed.connect(self.updateModel)
        self.tt.unsavedChnages.connect(self._unsavedChanges)
        self.enableSpindleLoad.emit(False)
        LOG.info(f"__init__() {self.status.allHomed()=}, {self.status.all_axes_homed.value=}")
    
    def _onInterpStateChange(self, state):
        self._emitTableEnableSignal()

    def _onTaskStateChange(self, state):
        self._emitTableEnableSignal()

    def _emitTableEnableSignal(self, *args):
        cond = self.stat.task_mode != cnc.MODE_AUTO and self.stat.interp_state == cnc.INTERP_IDLE #and self.stat.state == cnc.RCS_DONE
        enable_load_spindle = cond and self.stat.task_state == cnc.STATE_ON and self.status.all_axes_homed.value
        self.enableTable.emit(cond)
        self.enableSpindleLoad.emit(enable_load_spindle)

    def _unsavedChanges(self, tcId, value: bool):
        if tcId != self.changer_id:
            return
        
        self.unsaved_changes = value
        self.unsavedChanges.emit(value)
    
    def rowCount(self, *args):
        return len(self.model_data)

    def columnCount(self, *args):
        return len(self.column_headers)

    def refreshModel(self):
        self.beginResetModel()
        self.endResetModel()

    def updateModel(self, tc_id: int, row_headers: list, data: list):
        # LOG.info(f"updateModel() on TC#{self.changer_id}: {row_headers}")

        if tc_id != self.changer_id:
            return

        self.beginResetModel()
        self.model_data = data
        if row_headers:
            self.row_headers = row_headers
        self.endResetModel()

    def data(self, index, role):
        row, column = index.row(), index.column()

        if role == Qt.DisplayRole:
            if column == 1 and isinstance(self.model_data[row][column], (tuple, list)):
                return self.model_data[row][column][1]
            return self.model_data[row][column]
        
        if role == Qt.DecorationRole:
            if column == 1:
                if isinstance(self.model_data[row][column], (tuple, list)):
                    tool_icon = self.model_data[row][column][0]
                    tool_icon_px = QPixmap()
                    tool_icon_px.loadFromData(tool_icon)
                    return QIcon(tool_icon_px)
            
                # return QIcon(icon_abs_path('add_button'))
                return self.default_tool_icon
            
        if role == Qt.BackgroundRole and self.current_tool_bg:
            if self.stat.tool_in_spindle == self.model_data[row][0]:
                return self.current_tool_bg
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical and self.row_headers:
                return self.row_headers[section]
            elif orientation == Qt.Horizontal and self.column_headers:
                return self.column_headers[section]
            
        if role == Qt.BackgroundRole:
            if orientation == Qt.Vertical and self.row_headers:
                if self.model_data and self.model_data[section][0]:
                    return self.occupied_pocket_bg
                else:
                    return self.vacant_pocket_bg
    
    def swapRows(self, row1, row2):
        self.beginResetModel()
        self.model_data[row1], self.model_data[row2] = self.model_data[row2], self.model_data[row1]
        self.endResetModel()
        self._updateToolChanger({
            self.row_headers[row1]: self.model_data[row1][0],
            self.row_headers[row2]: self.model_data[row2][0],
        })

    def updateRow(self, row, data):
        self.beginResetModel()
        self.model_data[row] = data
        self.endResetModel()
        self._updateToolChanger({self.row_headers[row]: data[0]})

    def insertTool(self, tcId, row, data):
        if tcId != self.changer_id:
            return        
        self.updateRow(row, data)

    def clearRows(self, rows: Union[list, int]) -> None:
        self.beginResetModel()

        if isinstance(rows, (tuple, list)):
            for row in rows:
                self.model_data[row] = self.empty_row
        elif isinstance(rows, int):
            self.model_data[rows] = self.empty_row

        self.endResetModel()
        self._updateToolChanger()

    def _updateToolChanger(self, data: dict = None):
        if data:
            self.tt.updateToolChanger(self.changer_id,data)
        else:
            data_range = range(len(self.model_data))
            self.tt.updateToolChanger(
                self.changer_id,
                { self.row_headers[i]: self.model_data[i][0] for i in data_range }
            )

    def toolDataFromRow(self, row) -> list:
        try:
            return self.model_data[row]
        except IndexError:
            return []
        
    def toolNumberList(self, rows: tuple) -> tuple:
        try:
            return tuple(self.model_data[i][0] for i in rows)
        except IndexError:
            return tuple()
        
    def toolNumberFromRow(self, row: int) -> int:
        try:
            return self.model_data[row][0]
        except IndexError:
            return None

    def saveToolTable(self, cmd_reload_table=True):
        pockets = [(pn, self.model_data[i][0]) for i, pn in enumerate(self.row_headers)]
        pocket_data = dict(pockets)
        self.tt.saveToolChangerTable(self.changer_id, pocket_data, cmd_reload_table)
        return True

    def clearToolTable(self):
        self.beginResetModel()
        row_count = self.rowCount()
        self.model_data = [self.empty_row] * row_count
        self.endResetModel()
        return True

    def loadToolTable(self):
        self.tt.getToolChangerTable(self.changer_id)
        return True


class ToolChangerTableView(QTableView):
    QICON_SIZE = QSize(28, 28)

    openDialog = pyqtSignal(int, int)
    toolSelected = pyqtSignal(int)
    exchangeTool = pyqtSignal(list)

    singleRowSelected = pyqtSignal(bool)
    multipleRowsSelected = pyqtSignal(bool)
    enableDelete = pyqtSignal(bool)
    enableLeftToRightExchange = pyqtSignal(bool)
    enableRigthToLeftExchange = pyqtSignal(bool)
    enableReload = pyqtSignal(bool)
    enableLoadSpindle = pyqtSignal(bool)
    enableMultiSelect = pyqtSignal(bool)
    enableSave = pyqtSignal(bool)
    enableSwapping = pyqtSignal(bool)

    def __init__(self, parent=None, changer_id: int = None):
        super(ToolChangerTableView, self).__init__(parent)

        self.changer_id = changer_id or 1
        self.table_model = TableModel(self.changer_id)
        self.setModel(self.table_model)
        self.selection_model = self.selectionModel()

        self.enable_spindle_load = False
        self.tbale_enabled = True

        header = self.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.setCornerButtonEnabled(False)
        
        self.select_tool_dialog = getDialog('select_tool')

        self.doubleClicked.connect(self.onDoubleClick)
        self.table_model.model_changed.connect(self.onModelChange)
        self.table_model.unsavedChanges.connect(self.enableSave.emit)
        self.table_model.enableSpindleLoad.connect(self._enableLoadSpindle)
        self.table_model.enableTable.connect(self._enableTable)
        self.selection_model.selectionChanged.connect(self.onSelectionChanged)

        if self.select_tool_dialog:
            self.openDialog.connect(self.select_tool_dialog.showDialog)
            self.select_tool_dialog.toolData.connect(self.table_model.insertTool)

        # if not IN_DESIGNER:
        #     QTimer.singleShot(1000, self.table_model.loadToolTable)
        QTimer.singleShot(1000, self.table_model.loadToolTable)

    def _openToolSelectDialog(self):
        row = self.selectedRow()
        if row >= 0:
            self.openDialog.emit(self.changer_id, row)

    def _enableLoadSpindle(self, value: bool):
        row_count = len(self.selectedRows())
        self.enable_spindle_load = value
        self.enableLoadSpindle.emit(value and row_count == 1)

    def _enableTable(self, value: bool):
        self.tbale_enabled = value
        self.setEnabled(value)

        if value == False:
            self.enableDelete.emit(False)
            self.enableLeftToRightExchange.emit(False)
            self.enableRigthToLeftExchange.emit(False)
            self.enableLoadSpindle.emit(False)
            self.enableSave.emit(False)
            self.enableSwapping.emit(False)
        else:
            self.enableSave.emit(self.table_model.unsaved_changes)
            self.onSelectionChanged()
        
        self.enableReload.emit(value)
        self.enableMultiSelect.emit(value)

    def onModelChange(self):
        self.setIconSize(self.QICON_SIZE)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def keyPressEvent(self, event):
        if not self.tbale_enabled:
            return
        
        key = event.key()
        if key in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Space):
            self._openToolSelectDialog()
        elif key == Qt.Key_Delete:
            self.deleteSelectedTools()
        elif key == Qt.Key_L:
            self.loadSelectedTool()
        elif key == Qt.Key_R:
            self.loadToolTable()
        elif key == Qt.Key_S:
            self.saveToolTable()
        else:
            super().keyPressEvent(event)

    @pyqtSlot()
    def onDoubleClick(self):
        self._openToolSelectDialog()    

    def onSelectionChanged(self, *args):
        selected_rows = self.selectedRows()
        row_count = len(selected_rows)        
        toolno = self.table_model.toolNumberFromRow(selected_rows[0]) if row_count > 0 else None
        selection_mode = self.selectionMode()

        self.enableDelete.emit(row_count >= 1)
        self.enableSwapping.emit(selection_mode == self.MultiSelection and row_count > 1)
        self.enableLoadSpindle.emit(self.enable_spindle_load and row_count == 1 and toolno)

    @pyqtSlot(bool)
    def toggleSelectionMode(self, *args):
        selection_mode = self.selectionMode()

        if selection_mode == self.SingleSelection:
            self.setSelectionMode(self.MultiSelection)
        else:
            self.setSelectionMode(self.SingleSelection)
        
        self.selection_model.clearSelection()

    @pyqtSlot()
    def swapTools(self):
        selection = self.selection_model.selection()
        first_row = selection.first().indexes()[0].row()
        last_row = selection.last().indexes()[0].row()

        self.table_model.swapRows(first_row, last_row)
        self.selection_model.clearSelection()

    @pyqtSlot()
    def transferTool(self):
        row = self.selectedRow()
        if row < 0:
            return
        
        tool_data = self.table_model.toolDataFromRow(row)
        self.exchangeTool.emit(tool_data)
        self.table_model.clearRows(row)
        self.selection_model.clearSelection()

    @pyqtSlot(list)
    def recieveTool(self, tool_data):
        row = self.selectedRow()
        if row < 0:
            return
        
        self.table_model.updateRow(row, tool_data)
        self.selection_model.clearSelection()

    @pyqtSlot()
    def saveToolTable(self):
        if not self.confirmAction("Do you want to save changes and\n"
                                  "load tool table into LinuxCNC?"):
            return
        self.selection_model.clearSelection()
        self.table_model.saveToolTable()

    @pyqtSlot()
    def loadToolTable(self):
        if not self.confirmAction("Do you want to re-load the tool table?\n"
                                  "All unsaved changes will be lost."):
            return
        self.table_model.loadToolTable()


    @pyqtSlot()
    def deleteSelectedTools(self):
        """Delete the currently selected items"""
        selected_rows = self.selectedRows()
        if not selected_rows:
            return

        warning = None        
        tool_in_spindle = self.table_model.stat.tool_in_spindle
        selected_tools = self.table_model.toolNumberList(selected_rows)
        rows_to_remove = []
        tools_to_remove = []

        for toolno, row in zip(selected_tools, selected_rows):
            if toolno and toolno != tool_in_spindle:
                tools_to_remove.append(toolno)
                rows_to_remove.append(row)

            if toolno == tool_in_spindle:
                warning = QMessageBox(QMessageBox.Warning,
                    "Can't delete current tool!",
                    f"Tool <b>#{toolno}</b> is currently loaded in the spindle.\n",
                    QMessageBox.Ok,
                    parent=self)
        
        if warning:
            warning.show()

        if not rows_to_remove:
            return

        tools_to_delete = ', '.join(tuple(f"<b>T{t}</b>" for t in tools_to_remove))
        if not self.confirmAction(f'Are you sure you want to delete {tools_to_delete}?\n'):
            return

        self.table_model.clearRows(rows_to_remove)
        self.selection_model.clearSelection()

    @pyqtSlot()
    def clearToolTable(self, confirm=True):
        """Remove all items from the model"""
        if confirm and not self.confirmAction("Do you want to delete the whole tool table?"):
            return

        self.selection_model.clearSelection()
        self.table_model.clearToolTable()

    @pyqtSlot()
    def addTool(self):
        """Loads new item to the model"""
        self._openToolSelectDialog()

    @pyqtSlot()
    def loadSelectedTool(self):
        """Loads the tool from the selected row in the spindle"""

        current_row = self.selectedRow()
        if current_row == -1:
            return

        toolno = self.table_model.toolNumberFromRow(current_row)
        if toolno:
            issue_mdi(f"T{toolno} M6")
        
        self.selection_model.clearSelection()
    
    def selectedRow(self):
        """Returns the row number of the currently selected row, or 0"""

        selected_rows = self.selectedRows()
        if not selected_rows:
            return -1        
        return selected_rows[0]
    
    def selectedRows(self):
        """Returns the row number of the currently selected row, or 0"""
        return tuple(r.row() for r in self.selection_model.selectedRows(0))

    def onClick(self, index):
        self._openToolSelectDialog()

    def confirmAction(self, message):
        box = QMessageBox.question(self,
                        'Confirm Action',
                        message,
                        QMessageBox.Yes,
                        QMessageBox.No)

        return box == QMessageBox.Yes

    @Property(int)
    def toolChangerId(self):
        return self.changer_id

    @toolChangerId.setter
    def toolChangerId(self, value):
        self.changer_id = value
        self.table_model.changer_id = value

    @Property(QColor)
    def currentToolBackground(self):
        return self.table_model.current_tool_bg or QColor()

    @currentToolBackground.setter
    def currentToolBackground(self, color):
        self.table_model.current_tool_bg = color

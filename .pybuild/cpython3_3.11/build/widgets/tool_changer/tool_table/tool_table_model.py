import os
from typing import Union
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtCore import Qt, QAbstractTableModel, pyqtSignal
import linuxcnc as cnc


from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.plugins import getPlugin
# from craftisan.ui.dialogs.tool_db.select_tool import SelectToolDialog


LOG = getLogger(__name__)

IN_DESIGNER = os.getenv('DESIGNER', False)

COLUMN_HEADERS = ('#', 'Description', 'Diam.', 'Lenght')

class TableModel(QAbstractTableModel):
    current_tool_bg = QColor('#285c25')
    vacant_pocket_bg = QColor('#2c662d')
    occupied_pocket_bg = QColor('#965a2f')
    default_tool_icon = None
    empty_row = (None, 'Add tool...', None, None, None)
    unsaved_changes_all = False

    model_changed = pyqtSignal()
    unsavedChanges = pyqtSignal(bool)
    unsavedChangesAll = pyqtSignal(bool)
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
        self.tt = getPlugin('tooltable')
        self.stat = self.status.stat

        self.status.tool_in_spindle.notify(self.refreshModel)
        self.status.interp_state.notify(self._emitTableEnableSignal)
        self.status.task_state.notify(self._emitTableEnableSignal)
        self.status.task_mode.notify(self._emitTableEnableSignal)
        self.status.homed.notify(self._emitTableEnableSignal)
        self.tt.toolchanger_changed.connect(self.updateModel)
        self.tt.unsavedChnages.connect(self._unsavedChanges)
        self.tt.unsavedChnagesAll.connect(self._unsavedChangesAll)
        self.enableSpindleLoad.emit(False)

    def _emitTableEnableSignal(self, *args):
        cond = self.stat.task_mode != cnc.MODE_AUTO and self.stat.interp_state == cnc.INTERP_IDLE #and self.stat.state == cnc.RCS_DONE
        all_axes_homed = (self.stat.homed.count(1) == self.stat.joints)
        enable_load_spindle = cond and self.stat.task_state == cnc.STATE_ON and all_axes_homed
        self.enableTable.emit(cond)
        self.enableSpindleLoad.emit(enable_load_spindle)

        # LOG.info("_emitTableEnableSignal green<%r, %r, %r, %r, %r>", self.stat.task_mode, self.stat.interp_state, self.stat.task_state, all_axes_homed, enable_load_spindle)

    def _unsavedChanges(self, tcId, value: bool):
        if tcId != self.changer_id:
            return
        
        self.unsaved_changes = value
        self.unsavedChanges.emit(value)

    def _unsavedChangesAll(self, value: bool):        
        self.unsaved_changes_all = value
        self.unsavedChangesAll.emit(value)
    
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
                    # tool_icon_px = QPixmap()
                    # tool_icon_px.loadFromData(tool_icon)
                    return QIcon(tool_icon)
            
                # return QIcon(icon_abs_path('add_button'))
                return self.default_tool_icon
        if role == Qt.FontRole and column == 1:
            font = QFont()
            font.setFamily('Roboto')
            font.setBold(True)
            font.setPointSizeF(12)
            return font
            
        if role == Qt.BackgroundRole and self.current_tool_bg:
            if self.stat.tool_in_spindle == self.model_data[row][0]:
                return self.current_tool_bg
            
        # if role == Qt.ForegroundRole and self.current_tool_bg:
        #     if self.stat.tool_in_spindle == self.model_data[row][0]:
        #         return self.current_tool_bg
    
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
            # LOG.info(f"toolNumberFromRow[{self.changer_id}] -> {self.model_data[row][0]=}, {row=}")
            # toolno = self.model_data[row][0] if row is not None else -1
            # variables = ", ".join(tuple(f"{k}={v}" for k, v in locals().items() if k != 'self'))
            # LOG.info(f"toolNumberFromRow[{self.changer_id}] -> {variables}")
            return self.model_data[row][0] if row is not None else -1
        except IndexError:
            return -1

    def saveToolTable(self, cmd_reload_table=True):
        pockets = [(pn, self.model_data[i][0]) for i, pn in enumerate(self.row_headers)]
        pocket_data = dict(pockets)
        self.tt.saveToolChangerTable(self.changer_id, pocket_data, cmd_reload_table)
        return True

    def saveToolChangers(self):
        self.tt.saveToolChangers()
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


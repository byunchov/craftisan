import os
from PyQt5.QtWidgets import QHeaderView, QTableView, QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot, QTimer, QModelIndex
from qtpy.QtCore import Property

from qtpyvcp.actions.machine_actions import issue_mdi
from qtpyvcp.widgets.dialogs import getDialog
from qtpyvcp.utilities.logger import getLogger
from widgets.tool_changer.tool_table import TableModel

IN_DESIGNER = os.getenv('DESIGNER', False)

LOG = getLogger(__name__)

class ToolChangerTableView(QTableView):
    icon_size = QSize(*(48,)*2)

    openDialog = pyqtSignal(int, int)
    toolSelected = pyqtSignal(int)
    exchangedTool = pyqtSignal(tuple)
    transferedTool = pyqtSignal(tuple)
    selectedRowChanged = pyqtSignal(int, int)

    singleRowSelected = pyqtSignal(bool)
    multipleRowsSelected = pyqtSignal(bool)
    enableExchange = pyqtSignal(bool)
    enableDelete = pyqtSignal(bool)
    enableToolTransfer = pyqtSignal(bool)
    enableReload = pyqtSignal(bool)
    enableLoadSpindle = pyqtSignal(bool)
    enableMultiSelect = pyqtSignal(bool)
    enableSave = pyqtSignal(bool)
    enableSaveAll = pyqtSignal(bool)
    enableSwapping = pyqtSignal(bool)
    selectionModeToggled = pyqtSignal()

    def __init__(self, parent=None, changer_id: int = None):
        super(ToolChangerTableView, self).__init__(parent)

        self.changer_id = changer_id or 1
        self.table_model = TableModel(self.changer_id)
        self.setModel(self.table_model)
        self.selection_model = self.selectionModel()

        self.enable_spindle_load = False
        self.table_enabled = True
        self.local_row: int = None
        self.remote_row: int = None
        self.local_toolno: int = -1
        self.remote_toolno: int = -1

        header = self.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.setCornerButtonEnabled(False)
        
        self.select_tool_dialog = getDialog('select_tool')

        self.doubleClicked.connect(self.onDoubleClick)
        self.table_model.model_changed.connect(self.onModelChange)
        self.table_model.unsavedChanges.connect(self.enableSave.emit)
        self.table_model.unsavedChangesAll.connect(self.enableSaveAll.emit)
        self.table_model.enableSpindleLoad.connect(self._enableLoadSpindle)
        self.table_model.enableTable.connect(self._enableTable)
        self.selection_model.selectionChanged.connect(self.onSelectionChanged)
        self.clicked.connect(self.onClick)

        if self.select_tool_dialog:
            self.openDialog.connect(self.select_tool_dialog.showDialog)
            self.select_tool_dialog.toolData.connect(self.table_model.insertTool)

        if not IN_DESIGNER:
            QTimer.singleShot(1000, self.table_model.loadToolTable)
        # QTimer.singleShot(1000, self.table_model.loadToolTable)

    def _openToolSelectDialog(self):
        row = self.selectedRow()        
        self.openDialog.emit(self.changer_id, row)

    def _enableLoadSpindle(self, value: bool):
        row_count = len(self.selectedRows())
        self.enable_spindle_load = value
        self.enableLoadSpindle.emit(value and row_count == 1)

    def _enableTable(self, value: bool):
        self.table_enabled = value
        self.setEnabled(value)

        if value == False:
            self.enableDelete.emit(False)
            self.enableToolTransfer.emit(False)
            self.enableLoadSpindle.emit(False)
            self.enableSave.emit(False)
            self.enableSaveAll.emit(False)
            self.enableSwapping.emit(False)
        else:
            self.enableSave.emit(self.table_model.unsaved_changes)
            self.enableSaveAll.emit(self.table_model.unsaved_changes_all)
            self.onSelectionChanged()
        
        self.enableReload.emit(value)
        self.enableMultiSelect.emit(value)

    def onModelChange(self):
        self.setIconSize(self.icon_size)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def keyPressEvent(self, event):
        if not self.table_enabled:
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
            self.swapTools()
        elif key == Qt.Key_W:
            self.saveToolTable()
        elif key == Qt.Key_M:
            # self.toggleSelectionMode()
            self.selectionModeToggled.emit()
        else:
            super().keyPressEvent(event)

    @pyqtSlot()
    def onDoubleClick(self):
        self._openToolSelectDialog()
    
    def onClick(self, index: QModelIndex):
        # self.local_row = index.row()
        # self.local_toolno = self.table_model.toolNumberFromRow(self.local_row)
        # LOG.info(f"{self.local_row=}, {self.local_toolno=}, {index.data()=}, {index.column()=}")
        # self.selectedRowChanged.emit(self.local_row, self.local_toolno)
        pass

    def onSelectionChanged(self, *args):
        selected_rows = self.selectedRows()
        row_count = len(selected_rows)
        at_least_one_selected = row_count > 0
        single_row_selected = row_count == 1
        multiple_rows_selected = row_count > 1        
        first_row = selected_rows[0] if at_least_one_selected else None
        toolno = self.table_model.toolNumberFromRow(first_row) if at_least_one_selected else -1
        is_valid_toolno = (toolno is not None) and (toolno > 0)
        selection_mode = self.selectionMode()
        ena_spindle_load = self.enable_spindle_load and single_row_selected and is_valid_toolno

        self.enableDelete.emit(row_count >= 1 and is_valid_toolno)
        self.enableSwapping.emit(selection_mode == self.MultiSelection and multiple_rows_selected)
        self.enableLoadSpindle.emit(ena_spindle_load)
        # self.selectedRowChanged.emit(self.local_row, self.local_toolno)
        # LOG.info("onSelectionChanged() red<%r>", ena_spindle_load)

        # variables = ", ".join(tuple(f"{k}={v}" for k, v in locals().items() if k not in ('self', 'args')))
        # LOG.info(f"onSelectionChanged[{self.changer_id}] -> {variables}")
    
    def _shouldEnableExchange2(self, row: int, toolno=None):
        is_row_selected = row != None
        # if not toolno:
        #     toolno = self.table_model.toolNumberFromRow(row) if is_row_selected else 0
        is_valid_toolno = toolno != None and toolno > 0
        exchange_condition = bool(is_valid_toolno and is_row_selected)
        is_selected_left = self.selected_row_left != None
        is_selected_right = self.selected_row_right != None
        enable_ltr_echange = exchange_condition and is_selected_right
        enable_rtl_echange = exchange_condition and is_selected_left
        enable_echange = exchange_condition and is_selected_left and is_selected_right

        self.enableLeftToRightExchange.emit(enable_ltr_echange)
        self.enableRigthToLeftExchange.emit(enable_rtl_echange)
        self.enableExchange.emit(enable_echange)

        variables = ", ".join(tuple(f"{k}={v}" for k, v in locals().items() if k not in ('self', 'args')))
        LOG.info(f"_shouldEnableExchange[{self.changer_id}] -> {variables}")

    def _shouldEnableExchange(self, *args):
        is_valid_toolno_left = self.selected_toolno_left != None and self.selected_toolno_left > 0
        is_valid_toolno_right = self.selected_toolno_right != None and self.selected_toolno_right > 0
        is_selected_left = self._validateRowNumber(self.selected_row_left)
        is_selected_right = self._validateRowNumber(self.selected_row_right)
        transfer_confition_left = (is_valid_toolno_left and is_selected_left)
        transfer_confition_right = (is_valid_toolno_right and is_selected_right)
        enable_ltr_echange = transfer_confition_left and is_selected_right
        enable_rtl_echange = transfer_confition_right and is_selected_left
        enable_echange = is_valid_toolno_left and is_valid_toolno_right and is_selected_left and is_selected_right

        self.enableLeftToRightExchange.emit(enable_ltr_echange)
        self.enableRigthToLeftExchange.emit(enable_rtl_echange)
        self.enableExchange.emit(enable_echange)

        variables = ", ".join(tuple(f"{k}={v}" for k, v in locals().items() if k not in ('self', 'args')))
        class_variables = ", ".join(tuple(f"{k}={v}" for k, v in self.__dict__.items() if isinstance(v, int)))
        LOG.info(f"_shouldEnableExchange[{self.changer_id}] -> {variables}\n{class_variables=}")

    def _validateRowNumber(self, row: int) -> bool:
        return bool(row != None and row >= 0)

    @pyqtSlot(bool)
    def toggleSelectionMode(self, *args):
        selection_mode = self.selectionMode()

        if selection_mode == self.SingleSelection:
            self.setSelectionMode(self.MultiSelection)
        else:
            self.setSelectionMode(self.SingleSelection)
        
        # self.selection_model.clearSelection()
        self._postTransferProcedure()

    @pyqtSlot(int, int)
    def selectedRowLeft_old(self, row: int, toolno: int):
        self.selected_row_left = row
        self.selected_row_right = self.selectedRow()
        self.selected_toolno_left = toolno
        self.selected_toolno_right = self.table_model.toolNumberFromRow(self.selected_row_right)
        # enable_ltr_echange = row != self.selected_row_right and self.selected_row_right >= 0 and row >= 0
        # self.enableLeftToRightExchange.emit(enable_ltr_echange)
        # self._shouldEnableExchange(row)
        # self.exchangeStateChanged.emit()

        self._shouldEnableExchange()

        variables = ", ".join(tuple(f"{k}={v}" for k, v in locals().items() if k != 'self'))
        class_variables = ", ".join(tuple(f"{k}={v}" for k, v in self.__dict__.items() if isinstance(v, int) or v is None))
        LOG.info(f"selectedRowLeft[{self.changer_id}] -> {variables}\n{class_variables=}")

    @pyqtSlot(int, int)
    def selectedRowRight(self, row: int, toolno: int):        
        self.selected_row_left = self.selectedRow()
        self.selected_row_right = row
        self.selected_toolno_left = self.table_model.toolNumberFromRow(self.selected_row_left)
        self.selected_toolno_right = toolno
        # enable_ltr_echange = row != self.selected_row_left and self.selected_row_left >= 0 and row >= 0
        # self.enableRigthToLeftExchange.emit(enable_ltr_echange)
        # self._shouldEnableExchange(row)
        # self.exchangeStateChanged.emit()

        self._shouldEnableExchange()

        variables = ", ".join(tuple(f"{k}={v}" for k, v in locals().items() if k != 'self'))
        class_variables = ", ".join(tuple(f"{k}={v}" for k, v in self.__dict__.items() if isinstance(v, int) or v is None))
        # LOG.info(f"selectedRowRight[{self.changer_id}] -> {variables}\n{class_variables=}")

    @pyqtSlot(int, int)
    def selectedRowChange(self, row: int, toolno: int):
        self.remote_row = row
        self.remote_toolno = toolno

        is_valid_toolno_remote = toolno != None and toolno > 0
        is_valid_toolno_local = self.local_toolno != None and self.local_toolno > 0
        is_selected_remote = self._validateRowNumber(row)
        is_selected_local = self._validateRowNumber(self.local_row)
        transfer_confition_local = (is_valid_toolno_local and is_selected_local)
        transfer_confition_remote = (is_valid_toolno_remote and is_selected_remote)
        enable_transfer_local = transfer_confition_local and is_selected_remote
        enable_transfer_remote = transfer_confition_remote and is_selected_local
        enable_echange = is_valid_toolno_remote and is_valid_toolno_local and is_selected_local and is_selected_remote

        self.enableToolTransfer.emit(enable_transfer_local or enable_transfer_remote)
        self.enableExchange.emit(enable_echange)

        variables = ", ".join(tuple(f"{k}={v}" for k, v in locals().items() if k not in ('self', 'args')))
        # LOG.info(f"selectedRowChange[{self.changer_id}] -> {variables}")

    @pyqtSlot()
    def swapTools(self):
        selection = self.selection_model.selection()
        if len(selection.indexes()) <= 1:
            return
        
        first_row = selection.first().indexes()[0].row()
        last_row = selection.last().indexes()[0].row()

        self.table_model.swapRows(first_row, last_row)
        self.selection_model.clearSelection()
    
    def _postTransferProcedure(self):
        # self.selected_row_left = None
        # self.selected_row_right = None
        # self.selected_toolno_left = -1
        # self.selected_toolno_right = -1
        # self.enableLeftToRightExchange.emit(False)
        # self.enableRigthToLeftExchange.emit(False)
        self.enableToolTransfer.emit(False)
        self.enableExchange.emit(False)
        self.selection_model.clearSelection()

    @pyqtSlot()
    def transferTool(self):
        row = self.selectedRow()
        if row is None:
            return
        
        tool_data = self.table_model.toolDataFromRow(row)
        self.transferedTool.emit(tool_data)
        self.table_model.clearRows(row)
        self._postTransferProcedure()
    
    @pyqtSlot()
    def exchangeTool(self):
        row = self.selectedRow()
        if row is None:
            return
        
        tool_data = self.table_model.toolDataFromRow(row)
        self.exchangedTool.emit(tool_data)
        self._postTransferProcedure()

    @pyqtSlot(tuple)
    def recieveTool(self, tool_data):
        row = self.selectedRow()
        if row is None:
            return
        
        self.table_model.updateRow(row, tool_data)
        self._postTransferProcedure()

    @pyqtSlot(tuple)
    def sendTool(self, tool_data):
        row = self.selectedRow()
        if row is None:
            return
        old_tool_data = self.table_model.toolDataFromRow(row)
        self.transferedTool.emit(old_tool_data)
        self.table_model.updateRow(row, tool_data)
        self._postTransferProcedure()

    @pyqtSlot()
    def saveToolTable(self):
        if not self.confirmAction("Do you want to save changes and\n"
                                  "load tool table into LinuxCNC?"):
            return
        self.selection_model.clearSelection()
        self.table_model.saveToolTable()

    @pyqtSlot()
    def saveToolChangers(self):
        if not self.confirmAction("Do you want to save changes and\n"
                                  "reload tool table?"):
            return
        self.selection_model.clearSelection()
        self.table_model.saveToolChangers()

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
        if current_row is None:
            return

        toolno = self.table_model.toolNumberFromRow(current_row)
        if toolno and toolno > 0:
            issue_mdi(f"T{toolno} M6")
        
        self.selection_model.clearSelection()
    
    def selectedRow(self):
        """Returns the `row` number of the currently selected row, or `None` if no row are selected"""

        selected_rows = self.selectedRows()
        if not selected_rows:
            return None
        
        return selected_rows[0]
    
    def selectedRows(self):
        """Returns tuple of selected row numbers"""
        return tuple(r.row() for r in self.selection_model.selectedRows(0))

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

from qtpy.QtCore import Qt, Slot, Signal, Property, QSortFilterProxyModel
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QTableView, QHeaderView, QStyledItemDelegate, QDoubleSpinBox, QMessageBox, QMenu, QAction, QFileDialog
from widgets.laser_pos.laserpos_model import LaserPositionModel
from qtpyvcp.utilities.logger import getLogger
from pathlib import Path
import os

IN_DESIGNER = os.getenv('DESIGNER', False)
LOG = getLogger(__name__)


class ItemDelegate(QStyledItemDelegate):

    def __init__(self, limits):
        super(ItemDelegate, self).__init__()

        self._limits = limits
        self._padding = ' ' * 2

    def displayText(self, value, locale):
        if type(value) == float:
            return f"{value:.3f}"

        return "{}{}".format(self._padding, value)

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setFrame(False)
        editor.setAlignment(Qt.AlignCenter)
        editor.setDecimals(3)
        # editor.setStepType(QSpinBox.AdaptiveDecimalStepType)
        editor.setProperty('stepType', 1)  # stepType was added in 5.12

        if index.column() == 0:
            row = index.row()
            min_range = self._limits[row][0]
            max_range = self._limits[row][1]
        else:
            min_range = -1200.0
            max_range = 1200.0

        if min_range and max_range:
            editor.setRange(min_range, max_range)

        return editor


class LaserPositionTable(QTableView):
    file_path_changed = Signal(str)
    dimLChanged = Signal(float)
    dimHChanged = Signal(float)
    dimSChanged = Signal(float)
    ofsXChanged = Signal(float)
    ofsYChanged = Signal(float)
    ofsZChanged = Signal(float)
    enableInputs = Signal(bool)
    enableControls = Signal(bool)

    podChanged = Signal(str)
    consoleChanged = Signal(str)
    podPosChanged = Signal(str)
    consolePosChanged = Signal(str)

    def __init__(self, parent=None):
        super(LaserPositionTable, self).__init__(parent)
        self.lpos_model = LaserPositionModel(self)

        # Properties
        self._confirm_actions = False

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(0)
        self.proxy_model.setSourceModel(self.lpos_model)

        self.item_delegate = ItemDelegate(
            self.lpos_model.lpos.console_limits)
        self.setItemDelegate(self.item_delegate)

        self.setModel(self.proxy_model)

        # Appearance/Behaviour settings
        self.setSortingEnabled(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self._createActions()
        self._connectActions()

        self.lpos_model.lpos.errorNotifier.connect(self.onErrorMsg)
        self.lpos_model.lpos.enableInputs.connect(
            self.onEnableInput_Changed)
        self.lpos_model.lpos.currPosChanged.connect(self.onCurrPos_Changed)

        self.positioning = False
        self.file_path = ''

    def _createActions(self):
        self.clear_row_action = QAction("Clear Row", self)
        self.clear_table_action = QAction("Clear Table", self)
        self.load_table_action = QAction("Load Table", self)
        self.reload_table_action = QAction("Reload Table", self)
        self.save_table_action = QAction("Save Table", self)
        self.run_from_here_action = QAction("Start From Here", self)
        self.sort_row_asc_action = QAction("Sort Row Asc.", self)
        self.sort_row_dec_action = QAction("Sort Row Desc.", self)

    def _connectActions(self):
        # Connect File actions
        self.clear_row_action.triggered.connect(self.clearSelectedRow)
        self.clear_table_action.triggered.connect(self.clearPositionsTable)
        self.run_from_here_action.triggered.connect(self.startFromCurrRow)
        self.reload_table_action.triggered.connect(self.reloadPositionTable)
        self.load_table_action.triggered.connect(self.openFileDialog)
        self.save_table_action.triggered.connect(self.savePositionTable)
        self.sort_row_asc_action.triggered.connect(self.sortSelectedRow_Asc)
        self.sort_row_dec_action.triggered.connect(self.sortSelectedRow_Desc)


    def contextMenuEvent(self, event):
        if self.positioning:
            return
        
        row = self.selectedRow()
        table_stat = self.lpos_model.hasData()
        row_not_empty = self.lpos_model.hasRowData(row)

        menu = QMenu(self)

        if row_not_empty:
            menu.addAction(self.run_from_here_action)

            sort_menu = QMenu("Sort Row", menu)
            sort_menu.addAction(self.sort_row_asc_action)
            sort_menu.addAction(self.sort_row_dec_action)

            menu.addMenu(sort_menu)
            menu.addAction(self.clear_row_action)

        menu.addSeparator()
        menu.addAction(self.load_table_action)
        menu.addAction(self.reload_table_action)
        menu.addAction(self.save_table_action)
        menu.addAction(self.clear_table_action)

        self.clear_row_action.setEnabled(row_not_empty)
        self.run_from_here_action.setEnabled(row_not_empty)
        self.save_table_action.setEnabled(table_stat)
        self.reload_table_action.setEnabled(table_stat)
        self.clear_table_action.setEnabled(table_stat)
        self.sort_row_asc_action.setEnabled(row_not_empty)
        self.sort_row_dec_action.setEnabled(row_not_empty)

        menu.popup(event.globalPos())

    def keyPressEvent(self, event):
        if self.positioning:
            return

        key = event.key()
        if key == Qt.Key_L:
            self.openFileDialog()
        elif key == Qt.Key_R:
            self.reloadPositionTable()
        elif key == Qt.Key_S:
            self.startFromCurrRow()
        elif key == Qt.Key_W:
            self.savePositionTable()
        elif key == Qt.Key_D:
            self.clearSelectedRow()
        elif key == Qt.Key_Delete:
            self.clearPositionsTable()
        elif key == Qt.Key_Left:
            self.onPrevPod_Clicked()
        elif key == Qt.Key_Right:
            self.onNextPod_Clicked()
        elif key == Qt.Key_Up:
            self.onNextConsole_Clicked()
        elif key == Qt.Key_Down:
            self.onPrevConsole_Clicked()
        else:
            super().keyPressEvent(event)

    @Slot()
    def openFileDialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            '',
            "LaserPOS Files (*.lpos);;Text Files (*.txt)"
        )
        if filename:
            self.file_path = str(Path(filename))
            self.file_path_changed.emit(self.file_path)

    @Slot(str)
    def onErrorMsg(self, msg):
        QMessageBox.critical(self, 'Error', msg)

    def onCurrPos_Changed(self, pos):
        self.podPosChanged.emit('{:.3f}'.format(pos['y']))
        self.consolePosChanged.emit('{:.3f}'.format(pos['x']))
        self.podChanged.emit('{:.0f}'.format(pos['pod']))
        self.consoleChanged.emit('{:.0f}'.format(pos['console']))

    @Slot()
    def sortSelectedRow_Asc(self):
        row = self.selectedRow()
        self.lpos_model.sortSelectedRow(row)

    @Slot()
    def sortSelectedRow_Desc(self):
        row = self.selectedRow()
        self.lpos_model.sortSelectedRow(row, desc=True)

    @Slot()
    def savePositionTable(self):
        self.enableControls.emit(False)
        prompt = "Do you want to overwrite the file?"
        if not self.confirmAction(prompt):
            return
        self.lpos_model.savePositionTable()
        self.enableControls.emit(True)

    @Slot()
    def startFromCurrRow(self):
        row = self.selectedRow()

        if not self.lpos_model.hasRowData(row):
            return

        self.lpos_model.startFromRow(row)

    @Slot(str)
    def loadPositionTable(self, file_path):
        if not os.path.isfile(file_path):
            return

        prompt = "Do you want to load the table?\nAll unsaved changes will be lost."
        if not self.confirmAction(prompt):
            return
        self.lpos_model.loadPositionTable(file_path)
        self._notifyDimOfsChanges()

        self.enableControls.emit(self.lpos_model.hasData())

    def _notifyDimOfsChanges(self):
        for l in 'lhs':
            signal = getattr(self, f'dim{l.upper()}Changed')
            signal.emit(self.lpos_model.getDimValue(l))

        for l in 'xyz':
            signal = getattr(self, f'ofs{l.upper()}Changed')
            signal.emit(self.lpos_model.getOfsValue(l))

    @Slot()
    def reloadPositionTable(self):
        if self.file_path:
            self.loadPositionTable(self.file_path)

    @Slot()
    def clearSelectedRow(self):
        """Delete the currently selected item"""
        current_row = self.selectedRow()
        if current_row == -1:
            return

        prompt = "Are you sure you want to clear <b>{0}</b>?"
        row_text = self.lpos_model.lpos.row_labels[current_row].strip()
        prompt = prompt.format(row_text)

        if not self.confirmAction(prompt):
            return

        self.lpos_model.clearRow(current_row)

    @Slot()
    def clearPositionsTable(self, confirm=True):
        """Remove all items from the model"""
        if confirm:
            promt = "Do you want to clear the whole positions table?"
            if not self.confirmAction(promt):
                return

        self.file_path = ''
        self.lpos_model.clearTable()
        self._notifyDimOfsChanges()
        self.file_path_changed.emit(self.file_path)
        self.enableControls.emit(False)

    @Slot(bool)
    def onEnableInput_Changed(self, value):
        # self.setEnabled(value)
        self.positioning = not value
        self.enableInputs.emit(value)

    @Slot()
    def onStartPos_Clicked(self):
        if self.lpos_model.hasData() and not self.positioning:
            self.lpos_model.lpos.beginPositoning()

    @Slot()
    def onStopPos_Clicked(self):
        if not self.positioning:
            return

        self.lpos_model.lpos.endPositioning()

    @Slot()
    def onNextConsole_Clicked(self):
        if not self.positioning:
            return

        self.lpos_model.lpos.nextConsole()

    @Slot()
    def onPrevConsole_Clicked(self):
        if not self.positioning:
            return

        self.lpos_model.lpos.prevConsole()

    @Slot()
    def onNextPod_Clicked(self):
        if not self.positioning:
            return

        self.lpos_model.lpos.nextPod()

    @Slot()
    def onPrevPod_Clicked(self):
        if not self.positioning:
            return

        self.lpos_model.lpos.prevPod()

    @Slot(float)
    def onDimChange_L(self, value):
        self.lpos_model.setDimValue('l', value)

    @Slot(float)
    def onDimChange_H(self, value):
        self.lpos_model.setDimValue('h', value)

    @Slot(float)
    def onDimChange_S(self, value):
        self.lpos_model.setDimValue('s', value)

    @Slot(float)
    def onOfsChange_X(self, value):
        self.lpos_model.setOfsValue('x', value)

    @Slot(float)
    def onOfsChange_Y(self, value):
        self.lpos_model.setOfsValue('y', value)

    @Slot(float)
    def onOfsChange_Z(self, value):
        self.lpos_model.setOfsValue('z', value)

    @Slot(bool)
    def onManualPointer_Toggled(self, state):
        self.lpos_model.lpos.togglePointer(state)

    def selectedRow(self):
        """Returns the row number of the currently selected row, or 0"""
        return self.selectionModel().currentIndex().row()

    def confirmAction(self, message):
        if not self._confirm_actions:
            return True

        box = QMessageBox.question(self,
                                   'Confirm Action',
                                   message,
                                   QMessageBox.Yes,
                                   QMessageBox.No)
        return box == QMessageBox.Yes

    @Property(int)
    def currentRow(self):
        return self.selectedRow()

    @currentRow.setter
    def currentRow(self, row):
        self.selectRow(row)

    @Property(bool)
    def confirmActions(self):
        return self._confirm_actions

    @confirmActions.setter
    def confirmActions(self, confirm):
        self._confirm_actions = confirm

    @Property(QColor)
    def currentRowColor(self):
        return self.lpos_model.current_row_color

    @currentRowColor.setter
    def currentRowColor(self, color):
        self.lpos_model.current_row_color = color

    @Property(QColor)
    def currentRowBackground(self):
        return self.lpos_model.current_row_bg or QColor()

    @currentRowBackground.setter
    def currentRowBackground(self, color):
        self.lpos_model.current_row_bg = color

    @Property(QColor)
    def currentCellBackground(self):
        return self.lpos_model.current_cell_bg or QColor()

    @currentCellBackground.setter
    def currentCellBackground(self, color):
        self.lpos_model.current_cell_bg = color

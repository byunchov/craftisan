from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QColor, QBrush

from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.plugins import getPlugin

import math
import os

LOG = getLogger(__name__)
IN_DESIGNER = os.getenv('DESIGNER', False)


class LaserPositionModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(LaserPositionModel, self).__init__(parent)

        self.lpos = getPlugin('laserpos')
        # self.lpos = LaserPosTable()

        self.current_row_color = QColor(Qt.white)
        self.current_row_bg = QColor('#285c25')
        self.current_cell_bg = QColor('#2c662d')

        self.setColumnCount(len(self.lpos.column_labels))
        self.setRowCount(self.lpos._console_count)

        self.lpos.currConsoleChanged.connect(self.refreshModel)
        self.lpos.currPodChanged.connect(self.refreshModel)

    def refreshModel(self, callback=None):
        # refresh model so current row gets highlighted
        self.beginResetModel()
        if callable(callback):
            callback()
        self.endResetModel()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.lpos.column_labels[section]
        elif role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self.lpos.row_labels[section]
        
        if role == Qt.BackgroundRole and orientation == Qt.Vertical \
            and self.lpos.current_console == section:
            return QBrush(self.current_row_bg)

        return QStandardItemModel.headerData(self, section, orientation, role)

    def columnCount(self, parent=None):
        return self.lpos._col_count
        # return len(self.lpos.column_labels)

    def rowCount(self, parent=None):
        return self.lpos._console_count
        # return len(self.lpos.row_labels)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            row, col = index.row(), index.column()
            return self.lpos.positions_table[row][col]

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter | Qt.AlignRight

        elif role == Qt.TextColorRole:
            console = index.row()
            if self.lpos.current_console == console:
                return QBrush(self.current_row_color)
            
            return QStandardItemModel.data(self, index, role)

        elif role == Qt.BackgroundRole and self.current_row_bg is not None:
            console = index.row()
            col = index.column()
            pod_idx = self.lpos.current_pod + 1
            if self.lpos.current_console == console and pod_idx == col:
                return QBrush(self.current_cell_bg)
            elif self.lpos.current_console == console:
                return QBrush(self.current_row_bg)
            
            return QStandardItemModel.data(self, index, role)

        return QStandardItemModel.data(self, index, role)

    def setData(self, index, value, role):
        row, col = index.row(), index.column()
        self.lpos.positions_table[row][col] = value
        return True

    def clearRow(self, row):
        self.lpos.clearTableRow(row)
        self.refreshModel()

    def clearTable(self):
        self.refreshModel(self.lpos.clearTable)

    def hasData(self):
        rows = self.lpos.positions_table.values()
        return any([any(row) for row in rows])

    def hasRowData(self, row=0):
        if row < 0:
            return False
        
        return any(self.lpos.positions_table[row])

    def positionDataFromRow(self, row):    
        return self.lpos.positions_table[row]

    def savePositionTable(self):
        self.lpos.saveToFile()
        return True

    def loadPositionTable(self, file_path):
        self.beginResetModel()
        self.lpos.loadFromFile(file_path)
        self.endResetModel()
        return True
    
    def sortSelectedRow(self, row, *, desc=False):
        self.lpos.sortRow(row, desc=desc)
        self.refreshModel()
    
    def setDimValue(self, dim, value):
        dim_lower = dim.strip().lower()
        if dim_lower not in 'lhs':
            return
        
        curr_value = self.lpos.dimentions[dim_lower]
        if math.isclose(value, curr_value, rel_tol=1e-5):
            return
        
        if value >= 0:
            self.lpos.dimentions[dim_lower] = value

    def getDimValue(self, dim):
        dim_lower = dim.strip().lower()
        if dim_lower not in 'lhs':
            return
        return self.lpos.dimentions[dim_lower]
    
    def setOfsValue(self, ofs, value):
        ofs_lower = ofs.strip().lower()
        if ofs_lower not in 'xyz':
            return
        
        curr_value = self.lpos.offsets[ofs_lower]
        if math.isclose(value, curr_value, rel_tol=1e-5):
            return
        
        if value >= 0:
            self.lpos.offsets[ofs_lower] = value

    def getOfsValue(self, ofs):
        ofs_lower = ofs.strip().lower()
        if ofs_lower not in 'xyz':
            return
        return self.lpos.offsets[ofs_lower]
    
    def startFromRow(self, row):
        self.lpos.beginPositoning(row)

    def togglePointer(self, state):
        self.lpos.togglePointer(state)
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import (QApplication, QLineEdit, QLabel, QTableView, QWidget, 
QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy)
from delegates.program_variables_delegate import CustomDelegate


class ProgramDimentionsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.central_widget = QWidget(self)
        self.central_layout = QHBoxLayout(self.central_widget)
        vbox_ln_input = QVBoxLayout()
        vbox_hg_input = QVBoxLayout()
        vbox_th_input = QVBoxLayout()

        self.lenght_box = QLineEdit("0.0")
        self.height_box = QLineEdit("0.0")
        self.thickness_box = QLineEdit("0.0")
        spacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        spacer2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        spacer3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        lenght_lbl = QLabel("Lenght")
        height_lbl = QLabel("Height")
        thickness_lbl = QLabel("Thickness")

        vbox_ln_input.addWidget(lenght_lbl)
        vbox_ln_input.addWidget(self.lenght_box)
        vbox_ln_input.addItem(spacer1)

        vbox_hg_input.addWidget(height_lbl)
        vbox_hg_input.addWidget(self.height_box)
        vbox_hg_input.addItem(spacer2)

        vbox_th_input.addWidget(thickness_lbl)
        vbox_th_input.addWidget(self.thickness_box)
        vbox_th_input.addItem(spacer3)

        self.central_layout.addLayout(vbox_ln_input)
        self.central_layout.addLayout(vbox_hg_input)
        self.central_layout.addLayout(vbox_th_input)
        self.central_layout.setSpacing(10)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.central_layout)


class ProgramOffsetsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)

        self.lenght_box = QLineEdit("0.0")
        self.height_box = QLineEdit("0.0")
        self.thickness_box = QLineEdit("0.0")
        spacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        lenght_lbl = QLabel("Lenght")
        height_lbl = QLabel("Height")
        thickness_lbl = QLabel("Thickness")

        self.central_layout.addWidget(lenght_lbl)
        self.central_layout.addWidget(self.lenght_box)

        self.central_layout.addWidget(height_lbl)
        self.central_layout.addWidget(self.height_box)

        self.central_layout.addWidget(thickness_lbl)
        self.central_layout.addWidget(self.thickness_box)
        self.central_layout.addItem(spacer1)
        self.central_layout.setSpacing(10)
        self.central_layout.setContentsMargins(10, 10, 10, 10)

        self.setLayout(self.central_layout)



class ProgramOffsetsTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.central_widget = QWidget(self)
        self.central_layout = QHBoxLayout(self.central_widget)
        table_headers = tuple(f"Offeset {n}" for n  in 'XYZC')
        table_values = [[data for data in range(len(table_headers))]]
        
        table_widget = QTableWidget(self)
        table_widget.setColumnCount(len(table_headers))
        table_widget.setRowCount(1)
        table_widget.setHorizontalHeaderLabels(table_headers)
        
        for row, data in enumerate(table_values):
            for col, value in enumerate(data):
                value_item = QTableWidgetItem(str(value))
                table_widget.setItem(row, col, value_item)
        
        table_header = table_widget.horizontalHeader()
        table_header.setStretchLastSection(False)
        table_header.setSectionResizeMode(QHeaderView.Stretch)

        table_widget.verticalHeader().setHidden(True)
        # table_header.setHidden(True)

        self.central_layout.addWidget(table_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.central_layout)


class ProgramParametersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)
        self.tab_widget = QTabWidget(self)
        self.central_layout.addWidget(self.tab_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.central_layout)
        self._init_tabs()

    def _init_tabs(self):
        self.dim_widget = ProgramDimentionsWidget(self.tab_widget)
        self.ofs_widget = ProgramOffsetsWidget(self.tab_widget)
        self.var_widget = ProgramDimentionsWidget(self.tab_widget)
        self.tab_widget.addTab(self.dim_widget, "Dimetions")
        self.tab_widget.addTab(self.ofs_widget, "Offsets")
        self.tab_widget.addTab(self.var_widget, "Variables")

        self.tab_widget.setCurrentIndex(1)
        self.tab_widget.setTabVisible(2, False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # model = QStandardItemModel(4, 3)
    # for row in range(4):
    #     for col in range(3):
    #         item = model.item(row, col)
    #         if not item:
    #             item = QStandardItem()
    #         if col == 0:
    #             item.setData(True, Qt.DisplayRole)
    #             item.setData('b', Qt.UserRole)
    #         elif col == 1:
    #             item.setData(42, Qt.DisplayRole)
    #             item.setData('i', Qt.UserRole)
    #         else:
    #             item.setData(3.14, Qt.DisplayRole)
    #             item.setData('f', Qt.UserRole)
    #         model.setItem(row, col, item)

    
    # table.setItemDelegate(delegate)

    window = ProgramParametersWidget()
    window.setGeometry(100, 100, 400, 200)
    window.show()

    sys.exit(app.exec_())

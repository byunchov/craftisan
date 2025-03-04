from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from widgets.tool_changer.tool_table import ToolChangerTableView
from qtpyvcp.utilities.logger import getLogger

LOG = getLogger(__name__)

class TestDialog(QDialog):

    toolData = pyqtSignal(int, object)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # central_widget = QWidget(self)

        self.resize(1200, 800)
        self.setWindowTitle("Test dialog")

        vbox = QVBoxLayout(self)
        split_table_layout = QHBoxLayout()
        hbox = QHBoxLayout()
        action_layout = QVBoxLayout()

        self.linear_tc = ToolChangerTableView(changer_id=2)
        self.rotary_tc = ToolChangerTableView(changer_id=1)

        self.load_tc_1 = QPushButton("Load Linear TC")
        self.load_tc_2 = QPushButton("Load Rotary TC")
        self.multi_select = QPushButton("Swap tools")
        self.swap_button = QPushButton("Swap Rows")
        self.multi_select.setCheckable(True)
        self.swap_button.setEnabled(False)
        self.test_btn = QPushButton("Test")
        self.transfer_to_rotary = QPushButton("To Rotary")
        self.transfer_to_linear = QPushButton("To Linear")
        self.exchange_tools = QPushButton("Exchange")

        action_layout.addWidget(self.transfer_to_linear)
        action_layout.addWidget(self.transfer_to_rotary)
        action_layout.addWidget(self.exchange_tools)
        split_table_layout.addWidget(self.linear_tc)
        split_table_layout.addLayout(action_layout)
        split_table_layout.addWidget(self.rotary_tc)
        vbox.addLayout(split_table_layout)
        vbox.addLayout(hbox)

        hbox.addWidget(self.load_tc_1)
        hbox.addWidget(self.load_tc_2)
        hbox.addWidget(self.swap_button)
        hbox.addWidget(self.multi_select)
        hbox.addWidget(self.test_btn)
        self.multi_select.toggled.connect(self.linear_tc.toggleSelectionMode)
        self.multi_select.toggled.connect(lambda state: self.swap_button.setEnabled(state))
        self.swap_button.clicked.connect(self.linear_tc.swapTools)
        self.linear_tc.openDialog.connect(self.selectToolLinearTC)
        self.rotary_tc.openDialog.connect(self.selectToolRotaryTC)
        self.test_btn.clicked.connect(self.accept)

        self.setLayout(vbox)


    def selectToolLinearTC(self, row, toolno):
        LOG.info(f"selectToolLinearTC {row}, {toolno}")

        # text, ok = QInputDialog.getText(self, "Input Dialog", "Enter a value:", text=toolno)

        # if ok and text:
        #     print("Entered value:", text)
        #     self.linear_tc.table_model.updateRow(row, (text, f'Tool {text}', None, None))

    def selectToolRotaryTC(self, row, toolno):
        LOG.info(f"selectToolRotaryTC {row}, {toolno}")


        # text, ok = QInputDialog.getText(self, "Input Dialog", "Enter a value:", text=toolno)

        # if ok and text:
        #     print("Entered value:", text)
        #     self.rotary_tc.table_model.updateRow(row, (text, f'Tool {text}', None, None))


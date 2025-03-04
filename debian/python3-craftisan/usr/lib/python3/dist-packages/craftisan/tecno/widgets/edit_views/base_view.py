from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QSpinBox, QGroupBox, QDoubleSpinBox

from craftisan.tool_db.model import Tool
from craftisan.tecno.widgets.managers import DB_CHANGES


class BaseEditWidget(QWidget):
    SpindleDirection = ['M3 - Right', 'M4 - Left']

    def __init__(self, parent = None) -> None:
        super(BaseEditWidget, self).__init__(parent)

        self.tool = None

        # self.validators = [self.validateToolNumber]        

        # self.scrollArea = QScrollArea()
        # self.widget = QWidget()
        self.mainLayout = QVBoxLayout()

        self.toolIdFormLayout = QFormLayout()

        self.toolIdLbl = QLabel("Tool ID")
        self.toolIdInput = QSpinBox()
        self.toolIdInput.setRange(1, 10000)

        self.toolDescriptionLbl = QLabel("Description")
        self.toolDescriptionInput = QLineEdit()
        self.toolDescriptionInput.setPlaceholderText("Enter description...")
        self.toolDescriptionInput.setToolTip(Tool.formatedDescription.__doc__)

        self.toolIdFormLayout.addRow(self.toolIdLbl, self.toolIdInput)
        self.toolIdFormLayout.addRow(self.toolDescriptionLbl, self.toolDescriptionInput)
        self.mainLayout.addLayout(self.toolIdFormLayout)

        self.workFeedLayout = QFormLayout()
        self.workFeedGroup = QGroupBox("Feed Data")
        self.workFeedGroup.setLayout(self.workFeedLayout)

        self.dfltWorkFeedLbl = QLabel('Default Work Feed')
        self.dfltWorkFeedInput = QSpinBox()
        self.dfltWorkFeedInput.setRange(100, 20000)

        self.dfltPlungeFeedLbl = QLabel('Default Plunge Feed')
        self.dfltPlungeFeedInput = QSpinBox()
        self.dfltPlungeFeedInput.setRange(100, 14000)

        self.workFeedLayout.addRow(self.dfltWorkFeedLbl, self.dfltWorkFeedInput)
        self.workFeedLayout.addRow(self.dfltPlungeFeedLbl, self.dfltPlungeFeedInput)

        self.safetyDataLayout = QFormLayout()
        self.safetyDataGroup = QGroupBox("Safety Data")
        self.safetyDataGroup.setCheckable(True)
        self.safetyDataGroup.setChecked(False)
        self.safetyDataGroup.setLayout(self.safetyDataLayout)

        self.safetyOTDiaLbl = QLabel('Overall Tool Diameter')
        self.safetyOTDiaInput = QDoubleSpinBox()
        self.safetyOTDiaInput.setRange(0, 220)

        self.safetyOTLenLbl = QLabel('Overall Tool Lenght')
        self.safetyOTLenInput = QDoubleSpinBox()
        self.safetyOTLenInput.setRange(0, 300)

        self.safetyDataLayout.addRow(self.safetyOTDiaLbl, self.safetyOTDiaInput)
        self.safetyDataLayout.addRow(self.safetyOTLenLbl, self.safetyOTLenInput)        

        self.initUi()
        
        self.mainLayout.addWidget(self.workFeedGroup)
        self.mainLayout.addWidget(self.safetyDataGroup)

        self.mainLayout.addStretch()
        self.mainLayout.setSpacing(10)
        self.setLayout(self.mainLayout)

    def initUi(self):
        pass

    def fillToolData(self, tool):
        pass

    def validate(self):
        pass

    def validateToolNumber(self, toolId: int):
        if self.tool is None or toolId == self.tool.id:
            return
        
        newId = DB_CHANGES.validateToolId(toolId)

        if newId != toolId:
            self.toolIdInput.setValue(newId)

    def autoPopulateSafetyData(self):
        pass

    def connectSignals(self):
        self.toolIdInput.valueChanged[int].connect(self.validateToolNumber)
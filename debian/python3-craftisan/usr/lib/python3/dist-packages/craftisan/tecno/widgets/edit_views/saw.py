from PyQt5.QtWidgets import QFormLayout, QLabel, QComboBox, QSpinBox, QGroupBox, QDoubleSpinBox
from .base_view import BaseEditWidget

from craftisan.tool_db.model import Tool
from craftisan.utilities.misc import generate_icon


class SawTipDataWidget(BaseEditWidget):

    def __init__(self, parent = None) -> None:
        super(SawTipDataWidget, self).__init__(parent)

    def initUi(self):
        self.tipDataLayout = QFormLayout()
        self.tipDataGroup = QGroupBox("Saw Data")
        self.tipDataGroup.setLayout(self.tipDataLayout)

        self.tipDiaLbl = QLabel('[TD] Tool Diameter')
        self.tipDiaInput = QDoubleSpinBox()
        self.tipDiaInput.setRange(0, 220)

        self.tipLTLbl = QLabel('[LT] Tool Lenght')
        self.tipLTInput = QDoubleSpinBox()
        self.tipLTInput.setRange(20, 320)
        self.tipLTInput.setDecimals(4)

        self.sawThicknessLbl = QLabel('[D] Saw Thickness')
        self.sawThicknessInput = QDoubleSpinBox()
        self.sawThicknessInput.setRange(1, 20)

        self.tipLWLbl = QLabel('[MAXZ] Max depth')
        self.tipLWInput = QDoubleSpinBox()
        self.tipLWInput.setRange(10, 160)

        self.tipClearanceLbl = QLabel('[SZ] Tool clearance')
        self.tipClearanceInput = QDoubleSpinBox()
        self.tipClearanceInput.setRange(10, 160)

        self.tipDataLayout.addRow(self.tipLTLbl, self.tipLTInput)
        self.tipDataLayout.addRow(self.tipDiaLbl, self.tipDiaInput)
        self.tipDataLayout.addRow(self.tipLWLbl, self.tipLWInput)
        self.tipDataLayout.addRow(self.sawThicknessLbl, self.sawThicknessInput)
        self.tipDataLayout.addRow(self.tipClearanceLbl, self.tipClearanceInput)

        self.spindleDataLayout = QFormLayout()
        self.spindleDataGroup = QGroupBox("Spindle Data")
        self.spindleDataGroup.setLayout(self.spindleDataLayout)

        self.spindleDefRPMLbl = QLabel('Default RPM')
        self.spindleDefRPMInput = QSpinBox()
        self.spindleDefRPMInput.setRange(1200, 24000)
        self.spindleDefRPMInput.setSingleStep(100)
        
        self.spindleDirLbl = QLabel('Rotation Direction')
        self.spindleDirInput = QComboBox()
        self.spindleDirInput.addItems(self.SpindleDirection)

        self.spindleAccTimeLbl = QLabel('Tool Acc. Time')
        self.spindleAccTimeInput = QDoubleSpinBox()
        self.spindleAccTimeInput.setRange(1, 10)

        self.spindleDecTimeLbl = QLabel('Tool Dec. Time')
        self.spindleDecTimeInput = QDoubleSpinBox()
        self.spindleDecTimeInput.setRange(1, 10)

        self.spindleDataLayout.addRow(self.spindleDefRPMLbl, self.spindleDefRPMInput)
        self.spindleDataLayout.addRow(self.spindleDirLbl, self.spindleDirInput)
        self.spindleDataLayout.addRow(self.spindleAccTimeLbl, self.spindleAccTimeInput)
        self.spindleDataLayout.addRow(self.spindleDecTimeLbl, self.spindleDecTimeInput)

        self.mainLayout.addWidget(self.tipDataGroup)
        self.mainLayout.addWidget(self.spindleDataGroup)

    def setSafetyDia(self, value):
        if not self.safetyDataGroup.isChecked():
            self.safetyOTDiaInput.setValue(value)

    def setSafetyLT(self, value):
        if not self.safetyDataGroup.isChecked():
            self.safetyOTLenInput.setValue(value)

    def fillToolData(self, tool: Tool):
        self.tool = tool

        self.toolIdInput.setValue(tool.id)
        self.toolDescriptionInput.setText(tool.description)
        self.tipDiaInput.setValue(tool.getTipDiameter())
        self.tipLTInput.setValue(tool.getTipLT())
        self.tipLWInput.setValue(tool.getTipWorkDepth())
        self.sawThicknessInput.setValue(tool.ticknessSaw)
        self.tipClearanceInput.setValue(tool.AriaTool)
        self.spindleDefRPMInput.setValue(tool.defaultRPM)
        self.spindleDirInput.setCurrentIndex(tool.getTipSpindleDir())
        self.spindleAccTimeInput.setValue(tool.accTime)
        self.spindleDecTimeInput.setValue(tool.decTime)
        self.dfltWorkFeedInput.setValue(tool.defaultWorkFeed)
        self.dfltPlungeFeedInput.setValue(tool.defaultPenetrationFeed)
        self.safetyOTDiaInput.setValue(tool.magdiameter)
        self.safetyOTLenInput.setValue(tool.maglength)

        self.connectSignals()

    def validate(self):
        self.tool.id = self.toolIdInput.value()
        self.tool.description = self.toolDescriptionInput.text()
        self.tool.setTipDiameter(self.tipDiaInput.value())
        self.tool.setTipWorkDepth(self.tipLTInput.value())
        self.tool.setTipLT(self.tipLTInput.value())
        self.tool.ticknessSaw = self.sawThicknessInput.value()
        self.tool.AriaTool = self.tipClearanceInput.value()
        self.tool.defaultRPM = self.spindleDefRPMInput.value()
        self.tool.defaultRPM = self.spindleDefRPMInput.value()
        self.tool.setTipSpindleDir(self.spindleDirInput.currentIndex())
        self.tool.accTime = self.spindleAccTimeInput.value()
        self.tool.decTime = self.spindleDecTimeInput.value()
        self.tool.defaultWorkFeed = self.dfltWorkFeedInput.value()
        self.tool.defaultPenetrationFeed = self.dfltPlungeFeedInput.value()
        self.tool.magdiameter = self.safetyOTDiaInput.value() or self.tipDiaInput.value()
        self.tool.maglength = self.safetyOTLenInput.value() or self.tipLTInput.value()

        self.tool.icon = generate_icon(self.tool)

        return True, self.tool

    def autoPopulateSafetyData(self):
        pass

    def connectSignals(self):
        super().connectSignals()
        self.tipDiaInput.valueChanged[float].connect(self.setSafetyDia)
        self.tipLTInput.valueChanged[float].connect(self.setSafetyLT)

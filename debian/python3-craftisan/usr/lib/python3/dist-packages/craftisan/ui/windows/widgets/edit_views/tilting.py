from PyQt5.QtWidgets import QFormLayout, QLabel, QComboBox, QSpinBox, QGroupBox, QDoubleSpinBox
from .base_view import BaseEditWidget

from craftisan.tool_db.model import Tool
from craftisan.ui.windows.widgets.managers import DB_CHANGES
from craftisan.utilities.misc import generate_icon


class TiltingAggregateDataWidget(BaseEditWidget):

    def __init__(self, parent = None) -> None:
        super(TiltingAggregateDataWidget, self).__init__(parent)

    def initUi(self):
        self.tipDataLayout = QFormLayout()
        self.tipDataGroup = QGroupBox("Tip Data")
        self.tipDataGroup.setLayout(self.tipDataLayout)

        self.tipDiaLbl = QLabel('[TD] Tool Diameter')
        self.tipDiaInput = QDoubleSpinBox()
        self.tipDiaInput.setRange(0, 220)

        self.tipLTLbl = QLabel('[LT] Tool Lenght')
        self.tipLTInput = QDoubleSpinBox()
        self.tipLTInput.setRange(20, 320)
        self.tipLTInput.setDecimals(3)

        self.tipLAFulcrumLbl = QLabel('[LA] Fulcrum tip')
        self.tipLAFulcrumInput = QDoubleSpinBox()
        self.tipLAFulcrumInput.setRange(-100, 200)
        self.tipLAFulcrumInput.setDecimals(3)

        self.tipOffsetCLbl = QLabel('Offset C')
        self.tipOffsetCInput = QDoubleSpinBox()
        self.tipOffsetCInput.setRange(-9999, 9999)
        self.tipOffsetCInput.setDecimals(4)

        self.tipOFSZLbl = QLabel('[OFSZ] Corrector Z')
        self.tipOFSZInput = QDoubleSpinBox()
        self.tipOFSZInput.setRange(-100, 200)
        self.tipOFSZInput.setDecimals(4)
        
        self.tipOAZLbl = QLabel('[OAZ] Overall Dim. Z')
        self.tipOAZInput = QDoubleSpinBox()
        self.tipOAZInput.setRange(0, 100)
        self.tipOAZInput.setDecimals(4)

        self.tipClearanceLbl = QLabel('[SZ] Tool clearance')
        self.tipClearanceInput = QDoubleSpinBox()
        self.tipClearanceInput.setRange(10, 160)

        self.tipDataLayout.addRow(self.tipOFSZLbl, self.tipOFSZInput)
        self.tipDataLayout.addRow(self.tipLTLbl, self.tipLTInput)
        self.tipDataLayout.addRow(self.tipDiaLbl, self.tipDiaInput)
        self.tipDataLayout.addRow(self.tipLAFulcrumLbl, self.tipLAFulcrumInput)
        self.tipDataLayout.addRow(self.tipOffsetCLbl, self.tipOffsetCInput)
        self.tipDataLayout.addRow(self.tipOAZLbl, self.tipOAZInput)
        self.tipDataLayout.addRow(self.tipClearanceLbl, self.tipClearanceInput)

        self.spindleDataLayout = QFormLayout()
        self.spindleDataGroup = QGroupBox("Spindle Data")
        self.spindleDataGroup.setLayout(self.spindleDataLayout)

        self.spindleDefRPMLbl = QLabel('Default RPM')
        self.spindleDefRPMInput = QSpinBox()
        self.spindleDefRPMInput.setRange(1200, 24000)
        
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


        self.tipOFSZInput.setValue(tool.offsetZ)
        self.tipLTInput.setValue(tool.getTipLT())
        self.tipDiaInput.setValue(tool.getTipDiameter())
        self.tipLAFulcrumInput.setValue(tool.getTipLA())
        self.tipOffsetCInput.setValue(tool.getTipCOffset())
        self.tipOAZInput.setValue(tool.correctorZAria)
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
        old_dia = self.tool.getTipDiameter()
        old_dir = self.tool.getTipSpindleDir()

        self.tool.id = self.toolIdInput.value()
        self.tool.description = self.toolDescriptionInput.text()

        self.tool.setTipLA(self.tipLAFulcrumInput.value())
        self.tool.setTipCOffset(self.tipOffsetCInput.value())
        self.tool.correctorZAria = self.tipOAZInput.value()
        self.tool.setTipDiameter(self.tipDiaInput.value())
        self.tool.offsetZ = self.tipOFSZInput.value()
        self.tool.setTipLT(self.tipLTInput.value())
        self.tool.AriaTool = self.tipClearanceInput.value()
        self.tool.defaultRPM = self.spindleDefRPMInput.value()
        self.tool.setTipSpindleDir(self.spindleDirInput.currentIndex())
        self.tool.accTime = self.spindleAccTimeInput.value()
        self.tool.decTime = self.spindleDecTimeInput.value()
        self.tool.defaultWorkFeed = self.dfltWorkFeedInput.value()
        self.tool.defaultPenetrationFeed = self.dfltPlungeFeedInput.value()
        self.tool.magdiameter = self.safetyOTDiaInput.value()
        self.tool.maglength = self.safetyOTLenInput.value()

        if self.tool.getTipDiameter() != old_dia or self.tool.getTipSpindleDir() != old_dir:
            self.tool.icon = generate_icon(self.tool)

        return True, self.tool

    def autoPopulateSafetyData(self):
        pass

    def connectSignals(self):
        super().connectSignals()
        self.tipDiaInput.valueChanged[float].connect(self.setSafetyDia)
        self.tipLTInput.valueChanged[float].connect(self.setSafetyLT)
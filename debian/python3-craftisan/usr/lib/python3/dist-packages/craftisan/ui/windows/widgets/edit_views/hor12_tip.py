from PyQt5.QtWidgets import QFormLayout, QLabel, QComboBox, QSpinBox, QGroupBox, QDoubleSpinBox
from .base_view import BaseEditWidget

from craftisan.tool_db.model import Tool
from craftisan.ui.windows.widgets.managers import DB_CHANGES
from craftisan.utilities.misc import generate_icon


class Horizontal12TipDataWidget(BaseEditWidget):

    def __init__(self, parent = None) -> None:
        super(Horizontal12TipDataWidget, self).__init__(parent)

    def initUi(self):
        # Tip 1
        self.tip1DataLayout = QFormLayout()
        self.tip1DataGroup = QGroupBox("Tip 1 Data")
        self.tip1DataGroup.setLayout(self.tip1DataLayout)

        self.tip1DiaLbl = QLabel('[TD1] Tool Diameter')
        self.tip1DiaInput = QDoubleSpinBox()
        self.tip1DiaInput.setRange(0, 220)

        self.tip1LTLbl = QLabel('[LT1] Tool Lenght')
        self.tip1LTInput = QDoubleSpinBox()
        self.tip1LTInput.setRange(20, 320)
        self.tip1LTInput.setDecimals(3)

        self.tip1LAFulcrumLbl = QLabel('[LA1] Fulcrum tip')
        self.tip1LAFulcrumInput = QDoubleSpinBox()
        self.tip1LAFulcrumInput.setRange(-100, 200)
        self.tip1LAFulcrumInput.setDecimals(3)

        self.tip1OffsetCLbl = QLabel('Offset C')
        self.tip1OffsetCInput = QDoubleSpinBox()
        self.tip1OffsetCInput.setRange(-9999, 9999)
        self.tip1OffsetCInput.setDecimals(4)

        self.tip1DataLayout.addRow(self.tip1LTLbl, self.tip1LTInput)
        self.tip1DataLayout.addRow(self.tip1DiaLbl, self.tip1DiaInput)
        self.tip1DataLayout.addRow(self.tip1LAFulcrumLbl, self.tip1LAFulcrumInput)
        self.tip1DataLayout.addRow(self.tip1OffsetCLbl, self.tip1OffsetCInput)

        # Tip 2
        self.tip2DataLayout = QFormLayout()
        self.tip2DataGroup = QGroupBox("Tip 2 Data")
        self.tip2DataGroup.setLayout(self.tip2DataLayout)

        self.tip2DiaLbl = QLabel('[TD2] Tool Diameter')
        self.tip2DiaInput = QDoubleSpinBox()
        self.tip2DiaInput.setRange(0, 220)

        self.tip2LTLbl = QLabel('[LT2] Tool Lenght')
        self.tip2LTInput = QDoubleSpinBox()
        self.tip2LTInput.setRange(20, 320)
        self.tip2LTInput.setDecimals(3)

        self.tip2LAFulcrumLbl = QLabel('[LA2] Fulcrum tip')
        self.tip2LAFulcrumInput = QDoubleSpinBox()
        self.tip2LAFulcrumInput.setRange(-100, 200)
        self.tip2LAFulcrumInput.setDecimals(3)

        self.tip2OffsetCLbl = QLabel('Offset C')
        self.tip2OffsetCInput = QDoubleSpinBox()
        self.tip2OffsetCInput.setRange(-9999, 9999)
        self.tip2OffsetCInput.setDecimals(4)

        self.tip2DataLayout.addRow(self.tip2LTLbl, self.tip2LTInput)
        self.tip2DataLayout.addRow(self.tip2DiaLbl, self.tip2DiaInput)
        self.tip2DataLayout.addRow(self.tip2LAFulcrumLbl, self.tip2LAFulcrumInput)
        self.tip2DataLayout.addRow(self.tip2OffsetCLbl, self.tip2OffsetCInput)

        # Other data
        self.otherDataLayout = QFormLayout()
        self.otherDataGroup = QGroupBox("Other Data")
        self.otherDataGroup.setLayout(self.otherDataLayout)

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

        self.otherDataLayout.addRow(self.tipOFSZLbl, self.tipOFSZInput)
        self.otherDataLayout.addRow(self.tipOAZLbl, self.tipOAZInput)
        self.otherDataLayout.addRow(self.tipClearanceLbl, self.tipClearanceInput)

        # Spindle data
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

        self.mainLayout.addWidget(self.tip1DataGroup)
        self.mainLayout.addWidget(self.tip2DataGroup)
        self.mainLayout.addWidget(self.otherDataGroup)
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

        for i in range(2):
            getattr(self, f"tip{i+1}LTInput").setValue(tool.getTipLT(i))
            getattr(self, f"tip{i+1}DiaInput").setValue(tool.getTipDiameter(i))
            getattr(self, f"tip{i+1}LAFulcrumInput").setValue(tool.getTipLA(i))
            getattr(self, f"tip{i+1}OffsetCInput").setValue(tool.getTipCOffset(i))

        self.tipOFSZInput.setValue(tool.offsetZ)
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
        lengths = tuple(getattr(self, f"tip{i}LTInput").value() for i in range(1, 3))
        diameters = tuple(getattr(self, f"tip{i}DiaInput").value() for i in range(1, 3))
        fulcrums = tuple(getattr(self, f"tip{i}LAFulcrumInput").value() for i in range(1, 3))
        cOffsets = tuple(getattr(self, f"tip{i}OffsetCInput").value() for i in range(1, 3))
        
        self.tool.id = self.toolIdInput.value()
        self.tool.description = self.toolDescriptionInput.text()

        self.tool.setLengths(lengths)
        self.tool.setDiameters(diameters)
        self.tool.setFulcrumData(fulcrums)
        self.tool.setCOffsets(cOffsets)
        self.tool.correctorZAria = self.tipOAZInput.value()
        self.tool.offsetZ = self.tipOFSZInput.value()
        self.tool.AriaTool = self.tipClearanceInput.value()
        self.tool.defaultRPM = self.spindleDefRPMInput.value()
        self.tool.setTipSpindleDir(self.spindleDirInput.currentIndex())
        self.tool.accTime = self.spindleAccTimeInput.value()
        self.tool.decTime = self.spindleDecTimeInput.value()
        self.tool.defaultWorkFeed = self.dfltWorkFeedInput.value()
        self.tool.defaultPenetrationFeed = self.dfltPlungeFeedInput.value()
        self.tool.magdiameter = self.safetyOTDiaInput.value()
        self.tool.maglength = self.safetyOTLenInput.value()

        self.tool.icon = generate_icon(self.tool)

        return True, self.tool

    def autoPopulateSafetyData(self):
        pass

    def connectSignals(self):
        super().connectSignals()
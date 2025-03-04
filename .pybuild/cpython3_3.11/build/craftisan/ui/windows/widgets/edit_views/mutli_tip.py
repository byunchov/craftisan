from PyQt5.QtWidgets import QFormLayout, QLabel, QComboBox, QSpinBox, QGroupBox, QDoubleSpinBox
from .base_view import BaseEditWidget

from craftisan.tool_db.model import Tool
from craftisan.ui.windows.widgets.managers import DB_CHANGES
from craftisan.utilities.misc import generate_icon


class MultiTipDataWidget(BaseEditWidget):

    def __init__(self, parent = None) -> None:
        super(MultiTipDataWidget, self).__init__(parent)

    def initUi(self):
        # Tip 1
        self.tip1DataLayout = QFormLayout()
        self.tip1DataGroup = QGroupBox("Tip 1 Data")
        self.tip1DataGroup.setLayout(self.tip1DataLayout)

        self.tip1DiaLbl = QLabel('[TD1] Tool Diameter')
        self.tip1DiaInput = QDoubleSpinBox()
        self.tip1DiaInput.setRange(0.5, 220)

        self.tip1LTLbl = QLabel('[LT1] Tool Lenght')
        self.tip1LTInput = QDoubleSpinBox()
        self.tip1LTInput.setRange(20, 320)
        self.tip1LTInput.setDecimals(3)

        self.spindleDir1Lbl = QLabel('Spindle Dir.')
        self.spindleDir1Input = QComboBox()
        self.spindleDir1Input.addItems(self.SpindleDirection)

        self.tip1OffsetCLbl = QLabel('Offset C')
        self.tip1OffsetCInput = QDoubleSpinBox()
        self.tip1OffsetCInput.setRange(-9999, 9999)
        self.tip1OffsetCInput.setDecimals(4)

        self.tip1DataLayout.addRow(self.tip1DiaLbl, self.tip1DiaInput)
        self.tip1DataLayout.addRow(self.tip1LTLbl, self.tip1LTInput)
        self.tip1DataLayout.addRow(self.spindleDir1Lbl, self.spindleDir1Input)
        self.tip1DataLayout.addRow(self.tip1OffsetCLbl, self.tip1OffsetCInput)

        # Tip 2
        self.tip2DataLayout = QFormLayout()
        self.tip2DataGroup = QGroupBox("Tip 2 Data")
        self.tip2DataGroup.setLayout(self.tip2DataLayout)

        self.tip2DiaLbl = QLabel('[TD2] Tool Diameter')
        self.tip2DiaInput = QDoubleSpinBox()
        self.tip2DiaInput.setRange(0.5, 220)

        self.tip2LTLbl = QLabel('[LT2] Tool Lenght')
        self.tip2LTInput = QDoubleSpinBox()
        self.tip2LTInput.setRange(20, 320)
        self.tip2LTInput.setDecimals(3)

        self.spindleDir2Lbl = QLabel('Spindle Dir.')
        self.spindleDir2Input = QComboBox()
        self.spindleDir2Input.addItems(self.SpindleDirection)

        self.tip2OffsetCLbl = QLabel('Offset C')
        self.tip2OffsetCInput = QDoubleSpinBox()
        self.tip2OffsetCInput.setRange(-9999, 9999)
        self.tip2OffsetCInput.setDecimals(4)

        self.tip2DataLayout.addRow(self.tip2DiaLbl, self.tip2DiaInput)
        self.tip2DataLayout.addRow(self.tip2LTLbl, self.tip2LTInput)
        self.tip2DataLayout.addRow(self.spindleDir2Lbl, self.spindleDir2Input)
        self.tip2DataLayout.addRow(self.tip2OffsetCLbl, self.tip2OffsetCInput)

        # Tip 3
        self.tip3DataLayout = QFormLayout()
        self.tip3DataGroup = QGroupBox("Tip 3 Data")
        self.tip3DataGroup.setLayout(self.tip3DataLayout)

        self.tip3DiaLbl = QLabel('[TD3] Tool Diameter')
        self.tip3DiaInput = QDoubleSpinBox()
        self.tip3DiaInput.setRange(0.5, 220)

        self.tip3LTLbl = QLabel('[LT3] Tool Lenght')
        self.tip3LTInput = QDoubleSpinBox()
        self.tip3LTInput.setRange(20, 320)
        self.tip3LTInput.setDecimals(3)

        self.spindleDir3Lbl = QLabel('Spindle Dir.')
        self.spindleDir3Input = QComboBox()
        self.spindleDir3Input.addItems(self.SpindleDirection)

        self.tip3OffsetCLbl = QLabel('Offset C')
        self.tip3OffsetCInput = QDoubleSpinBox()
        self.tip3OffsetCInput.setRange(-9999, 9999)
        self.tip3OffsetCInput.setDecimals(4)

        self.tip3DataLayout.addRow(self.tip3DiaLbl, self.tip3DiaInput)
        self.tip3DataLayout.addRow(self.tip3LTLbl, self.tip3LTInput)
        self.tip3DataLayout.addRow(self.spindleDir3Lbl, self.spindleDir3Input)
        self.tip3DataLayout.addRow(self.tip3OffsetCLbl, self.tip3OffsetCInput)

        # Tip 4
        self.tip4DataLayout = QFormLayout()
        self.tip4DataGroup = QGroupBox("Tip 4 Data")
        self.tip4DataGroup.setLayout(self.tip4DataLayout)

        self.tip4DiaLbl = QLabel('[TD4] Tool Diameter')
        self.tip4DiaInput = QDoubleSpinBox()
        self.tip4DiaInput.setRange(0, 220)

        self.tip4LTLbl = QLabel('[LT4] Tool Lenght')
        self.tip4LTInput = QDoubleSpinBox()
        self.tip4LTInput.setRange(20, 320)
        self.tip4LTInput.setDecimals(3)

        self.spindleDir4Lbl = QLabel('Spindle Dir.')
        self.spindleDir4Input = QComboBox()
        self.spindleDir4Input.addItems(self.SpindleDirection)

        self.tip4OffsetCLbl = QLabel('Offset C')
        self.tip4OffsetCInput = QDoubleSpinBox()
        self.tip4OffsetCInput.setRange(-9999, 9999)
        self.tip4OffsetCInput.setDecimals(4)

        self.tip4DataLayout.addRow(self.tip4DiaLbl, self.tip4DiaInput)
        self.tip4DataLayout.addRow(self.tip4LTLbl, self.tip4LTInput)
        self.tip4DataLayout.addRow(self.spindleDir4Lbl, self.spindleDir4Input)
        self.tip4DataLayout.addRow(self.tip4OffsetCLbl, self.tip4OffsetCInput)


        self.spindleDataLayout = QFormLayout()
        self.spindleDataGroup = QGroupBox("Spindle Data")
        self.spindleDataGroup.setLayout(self.spindleDataLayout)

        self.tipClearanceLbl = QLabel('[SZ] Tool clearance')
        self.tipClearanceInput = QDoubleSpinBox()
        self.tipClearanceInput.setRange(10, 160)

        self.spindleDefRPMLbl = QLabel('Default RPM')
        self.spindleDefRPMInput = QSpinBox()
        self.spindleDefRPMInput.setRange(1200, 24000)
        
        self.spindleAccTimeLbl = QLabel('Tool Acc. Time')
        self.spindleAccTimeInput = QDoubleSpinBox()
        self.spindleAccTimeInput.setRange(1, 10)

        self.spindleDecTimeLbl = QLabel('Tool Dec. Time')
        self.spindleDecTimeInput = QDoubleSpinBox()
        self.spindleDecTimeInput.setRange(1, 10)

        self.spindleDataLayout.addRow(self.tipClearanceLbl, self.tipClearanceInput)
        self.spindleDataLayout.addRow(self.spindleDefRPMLbl, self.spindleDefRPMInput)
        self.spindleDataLayout.addRow(self.spindleAccTimeLbl, self.spindleAccTimeInput)
        self.spindleDataLayout.addRow(self.spindleDecTimeLbl, self.spindleDecTimeInput)

        for i in range(1, 5):
            self.mainLayout.addWidget(getattr(self, f"tip{i}DataGroup"))
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

        # # Tip 1
        # self.tip1LTInput.setValue(tool.getTipLT())
        # self.tip1DiaInput.setValue(tool.getTipDiameter())
        # self.spindleDir1Input.setCurrentIndex(tool.getTipSpindleDir())
        # self.tip1OffsetCInput.setValue(tool.getTipCOffset())

        # # Tip 2
        # self.tip2LTInput.setValue(tool.getTipLT(1))
        # self.tip2DiaInput.setValue(tool.getTipDiameter(1))
        # self.spindleDir2Input.setCurrentIndex(tool.getTipSpindleDir(1))
        # self.tip2OffsetCInput.setValue(tool.getTipCOffset(1))

        # # Tip 3
        # self.tip3LTInput.setValue(tool.getTipLT(2))
        # self.tip3DiaInput.setValue(tool.getTipDiameter(2))
        # self.spindleDir3Input.setCurrentIndex(tool.getTipSpindleDir(2))
        # self.tip3OffsetCInput.setValue(tool.getTipCOffset(2))

        # # Tip 4
        # self.tip4LTInput.setValue(tool.getTipLT(3))
        # self.tip4DiaInput.setValue(tool.getTipDiameter(3))
        # self.spindleDir4Input.setCurrentIndex(tool.getTipSpindleDir(3))
        # self.tip4OffsetCInput.setValue(tool.getTipCOffset(3))

        for i in range(4):
            getattr(self, f'tip{i+1}LTInput').setValue(tool.getTipLT(i))
            getattr(self, f'tip{i+1}DiaInput').setValue(tool.getTipDiameter(i))
            getattr(self, f'tip{i+1}OffsetCInput').setValue(tool.getTipCOffset(i) )
            getattr(self, f'spindleDir{i+1}Input').setCurrentIndex(tool.getTipSpindleDir(i))


        # Spindle
        self.tipClearanceInput.setValue(tool.AriaTool)
        self.spindleDefRPMInput.setValue(tool.defaultRPM)
        self.spindleAccTimeInput.setValue(tool.accTime)
        self.spindleDecTimeInput.setValue(tool.decTime)
        
        # Work feed
        self.dfltWorkFeedInput.setValue(tool.defaultWorkFeed)
        self.dfltPlungeFeedInput.setValue(tool.defaultPenetrationFeed)

        # Safety data
        self.safetyOTDiaInput.setValue(tool.magdiameter)
        self.safetyOTLenInput.setValue(tool.maglength)

        self.connectSignals()

    def validate(self):
        self.tool.id = self.toolIdInput.value()
        self.tool.description = self.toolDescriptionInput.text()

        lengths = tuple(getattr(self, f'tip{i}LTInput').value() for i in range(1, 5))
        diameters = tuple(getattr(self, f'tip{i}DiaInput').value() for i in range(1, 5))
        cOffsets = tuple(getattr(self, f'tip{i}OffsetCInput').value() for i in range(1, 5))
        directions = tuple(getattr(self, f'spindleDir{i}Input').currentIndex() for i in range(1, 5))

        self.tool.setLengths(lengths)
        self.tool.setDiameters(diameters)
        self.tool.setCOffsets(cOffsets)
        self.tool.setSpindleDirs(directions)

        self.tool.AriaTool = self.tipClearanceInput.value()
        self.tool.defaultRPM = self.spindleDefRPMInput.value()
        self.tool.defaultRPM = self.spindleDefRPMInput.value()
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

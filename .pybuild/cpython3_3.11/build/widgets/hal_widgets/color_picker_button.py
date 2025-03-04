from qtpy.QtWidgets import QPushButton, QColorDialog
from qtpy.QtCore import Slot, Signal
from PyQt5.QtGui import QColor


class QColorPickerButton(QPushButton):
    selectedColor = Signal(QColor)
    selectedColorInt = Signal(int)

    def __init__(self, parent=None):
        super(QColorPickerButton, self).__init__(parent)
        self.selected_color = None
        self.selected_color_int = 0

        self.clicked.connect(self.selectColor)

    def color2int(self, color: QColor):
        # colors = color.getRgb()
        # return (colors[0] << 16) + (colors[1] << 8) + colors[2]

        return int(color.name()[1:], 16)
    
    def int2color(self, color: int):
        return QColor(color)

    def selectColor(self):
        if self.selected_color is not None:
            self.selected_color = QColorDialog.getColor(self.selected_color)
        else:
            self.selected_color = QColorDialog.getColor()

        if self.selected_color is not None and self.selected_color.isValid():
            self.selected_color_int = self.color2int(self.selected_color)
            self.selectedColorInt.emit(self.selected_color_int)
            self.selectedColor.emit(self.selected_color)

            print(f"Color: #{self.selected_color_int:06x}")

    @Slot(int)
    def updateColor(self, color: int):
        self.selected_color_int = color
        self.selected_color = self.int2color(color)
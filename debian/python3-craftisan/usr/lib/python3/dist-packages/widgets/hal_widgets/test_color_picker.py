import sys
from PyQt5.QtWidgets import QApplication, QWidget, QColorDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QGraphicsDropShadowEffect
from PyQt5.QtCore import QEvent, Qt, QPointF, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPainter, QPen

UINT_MAX_SIZE = 16777215

class QColorPickerButton(QPushButton):
    selectedColor = pyqtSignal(QColor)

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
            self.selectedColor.emit(self.selected_color)

            print(f"Color: #{self.selected_color_int:06x}")

    @pyqtSlot(int)
    def updateColor(self, color: int):
        self.selected_color_int = color
        self.selected_color = self.int2color(color)


class QColorPreview(QWidget):
    def __init__(self, parent=None, color = None):
        super().__init__(parent)

        self.current_color = color or QColor(0)
        self.setFixedSize(28, 28)
        # shadow_effect = QGraphicsDropShadowEffect(offset=QPointF(4, 4), blurRadius=5)
        # self.setGraphicsEffect(shadow_effect)

    @pyqtSlot(QColor)
    def updatePreviewColor(self, color: QColor):
        self.current_color = color
        print(f"QColorPreview color {color.name()}")

    def updatePalete(self):
        pal = self.palette()
        pal.setColor(self.backgroundRole(), self.current_color)
        self.setPalette(pal)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Draw sunken border
        border_color = self.palette().color(self.backgroundRole()).darker(180)
        painter.setPen(QPen(border_color, 2.2))
        painter.drawRect(self.rect())

        # Fill with the current color
        painter.fillRect(self.rect().adjusted(1, 1, -1, -1), self.current_color)
        # painter.fillRect(self.rect(), self.current_color)
        
    
class HalQColorSpinBox(QSpinBox):

    def __init__(self, parent=None):
        super(HalQColorSpinBox, self).__init__(parent)

        self._value_pin = None
        self._enabled_pin = None
        self.selected_color = None
        self.selected_color_int = 0

        self._signed_int = True
        self.installEventFilter(self)
        self.setFocusPolicy(Qt.NoFocus)

        self.valueChanged.connect(self.onValueChanged)

    def color2int(self, color: QColor):
        colors = color.getRgb()
        return (colors[0] << 16) + (colors[1] << 8) + colors[2]
    
    def int2color(self, color: int):
        return QColor(color)

    def changeEvent(self, event):
        super(HalQColorSpinBox, self).changeEvent(event)
        if event == QEvent.EnabledChange and self._enabled_pin is not None:
            self._enabled_pin.value = self.isEnabled()

    def onValueChanged(self, value: int):
        print(f"Pin value will be set to #{value:06x}")

    def eventFilter(self, a0, a1: QEvent) -> bool:
        # if a0 is not self:
        #     return super().eventFilter(a0, a1)
        
        if a1.type() == QEvent.MouseButtonDblClick:
            ## When double clicked inside the Disabled QLineEdit of
            ## the SpinBox, this will enable it and set the focus on it
            # self.lineEdit().setEnabled(True)
            # self.setFocus()
            self.selectColor()
            print('Double click')
        elif a1.type() == QEvent.FocusOut:
            ## When you lose the focus, e.g. you click on other object
            ## this will diable the QLineEdit
            self.lineEdit().setEnabled(False)
        elif a1.type() == QEvent.KeyPress:
            ## When you press the Enter Button (Return) or the 
            ## Key Pad Enter (Enter) you will disable the QLineEdit
            if a1.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.lineEdit().setEnabled(False)
        return super().eventFilter(a0, a1)
    
    def selectColor(self):
        if self.selected_color is not None:
            self.selected_color = QColorDialog.getColor(self.selected_color)
        else:
            self.selected_color = QColorDialog.getColor()

        if self.selected_color is not None and self.selected_color.isValid():
            self.selected_color_int = self.color2int(self.selected_color)
            self._spinbox.setValue(self.selected_color_int)

            print(f"Color: #{self.selected_color_int:06x}")

class HalQColorSpinBox1(QWidget):
    def __init__(self, parent=None):
        super(HalQColorSpinBox1, self).__init__(parent)

        self._value_pin = None
        self._enabled_pin = None
        self._signed_int = True
        self.selected_color = None
        self.selected_color_int = 0

        self._spinbox = QSpinBox(self)
        self._color_dialog_btn = QColorPickerButton('...')
        self._color_preview = QColorPreview()

        self._spinbox.setMinimum(1)
        self._spinbox.setMaximum(UINT_MAX_SIZE)
        self._spinbox.setDisplayIntegerBase(16)
        self._spinbox.setPrefix("#")
        self._color_dialog_btn.setFixedWidth(32)

        self._layout = QHBoxLayout(self)

        self._layout.addWidget(self._color_preview)
        self._layout.addWidget(self._spinbox)
        self._layout.addWidget(self._color_dialog_btn)
        self.setLayout(self._layout)

        self._spinbox.valueChanged.connect(self.onValueChanged)
        self._spinbox.valueChanged.connect(self._color_dialog_btn.updateColor)
        # self._color_dialog_btn.clicked.connect(self.selectColor)
        self._color_dialog_btn.selectedColor.connect(self.setColor2)
        
        self._color_dialog_btn.selectedColor.connect(self._color_preview.updatePreviewColor)

    def color2int(self, color: QColor):
        colors = color.getRgb()
        return (colors[0] << 16) + (colors[1] << 8) + colors[2]
    
    def int2color(self, color: int):
        return QColor(color)

    def changeEvent(self, event):
        super(HalQColorSpinBox1, self).changeEvent(event)
        if event == QEvent.EnabledChange and self._enabled_pin is not None:
            self._enabled_pin.value = self.isEnabled()

    def onValueChanged(self, value: int):
        print(f"Pin value will be set to #{value:06x}")

    def setColor2(self, color: QColor):
        if color is not None and color.isValid():
            self._spinbox.setValue(self.color2int(color))
            # self._color_preview.setStyleSheet(f"background-color: {color.name()};")

    def selectColor(self):
        if self.selected_color is not None:
            self.selected_color = QColorDialog.getColor(self.selected_color)
        else:
            self.selected_color = QColorDialog.getColor()

        if self.selected_color is not None and self.selected_color.isValid():
            self.selected_color_int = self.color2int(self.selected_color)
            self._spinbox.setValue(self.selected_color_int)

            print(f"Color: #{self.selected_color_int:06x}")

            # self._color_preview.setStyleSheet(f"background-color: {self.selected_color.name()};")

            pal = self.palette()
            pal.setColor(self.backgroundRole(), self.selected_color)
            self.setPalette(pal)

class MainForm1(QWidget):
    def __init__(self):
        super(MainForm, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Form Switcher')
        self.setGeometry(100, 100, 400, 200)
        self.selected_color = None

        self.btn1 = QPushButton('First')
        self.color_lbl = QLabel(str(self.selected_color))

        self._layout = QVBoxLayout()

        self._layout.addWidget(self.color_lbl)
        self._layout.addWidget(self.btn1)
        self.setLayout(self._layout)

        self.btn1.clicked.connect(self.first)

    def first(self):
        if self.selected_color is not None:
            self.selected_color = QColorDialog.getColor(self.selected_color)
        else:
            self.selected_color = QColorDialog.getColor()

        if self.selected_color is not None and self.selected_color.isValid():
            self.color_lbl.setText(f"HEX: {self.selected_color.name()} RGB: {self.selected_color.getRgb()}")

class MainForm(QWidget):
    def __init__(self):
        super(MainForm, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Form Switcher')
        self.setGeometry(100, 100, 400, 200)
        self.selected_color = None

        self.spinbox = HalQColorSpinBox1()
        self._layout = QVBoxLayout()

        self._layout.addWidget(self.spinbox)
        self.setLayout(self._layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainForm()
    window.setGeometry(10, 100, 350, 600)
    window.show()
    sys.exit(app.exec_())

# (R≪16)+(G≪8)+B
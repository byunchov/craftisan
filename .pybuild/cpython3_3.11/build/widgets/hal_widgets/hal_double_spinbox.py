from qtpy.QtWidgets import QDoubleSpinBox
from qtpy.QtCore import QEvent, Slot

from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget


class HalQDoubleSpinBox(QDoubleSpinBox, HALWidget):
    """HAL DoubleSpinBox

    DoubleSpinBox for displaying and setting `float` HAL pin values.

    .. table:: Generated HAL Pins

        ========================= ========= =========
        HAL Pin Name              Type      Direction
        ========================= ========= =========
        qtpyvcp.spinbox.enable    bit       in
        qtpyvcp.spinbox.in        float     in
        qtpyvcp.spinbox.out       float     out
        ========================= ========= =========
    """
    def __init__(self, parent=None):
        super(HalQDoubleSpinBox, self).__init__(parent)

        self._value_pin = None
        self._enabled_pin = None

        self._signed_int = True

        self.valueChanged.connect(self.onCheckedStateChanged)

    def changeEvent(self, event):
        super(HalQDoubleSpinBox, self).changeEvent(event)
        if event == QEvent.EnabledChange and self._enabled_pin is not None:
            self._enabled_pin.value = self.isEnabled()

    def onCheckedStateChanged(self, checked):
        if self._value_pin is not None:
            self._value_pin.value = checked

    @Slot()
    def zero(self):
        self.setValue(0)

    def initialize(self):
        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

       # add spinbox.enable HAL pin
        self._enabled_pin = comp.addPin(f"{obj_name}.enable", "bit", "in")
        self._enabled_pin.value = self.isEnabled()
        self._enabled_pin.valueChanged.connect(self.setEnabled)

        # add spinbox.out HAL pin
        self._value_pin = comp.addPin(f"{obj_name}.out", "float", "out")
        self._value_pin.value = self.value()

        # add spinbox.in HAL pin
        self._set_value_pin = comp.addPin(f"{obj_name}.in", "float", "in")
        self._set_value_pin.valueChanged.connect(self.setValue)

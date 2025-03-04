
from qtpy.QtWidgets import QSpinBox
from qtpy.QtCore import QEvent, Signal

from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget


class HalQColorSpinBox(QSpinBox, HALWidget):
    """HAL SpinBox

    SpinBox for displaying and setting `u32` and `s32` HAL pin values.

    .. table:: Generated HAL Pins

        ============================= ========= =========
        HAL Pin Name                  Type      Direction
        ============================= ========= =========
        qtpyvcp.color_spinbox.enable  s32 | u32 in
        qtpyvcp.color_spinbox.in      s32 | u32 in
        qtpyvcp.color_spinbox.out     s32 | u32 out
        ============================= ========= =========

    Note:
        If the ``minimum`` value property is set to 0 or greater a u32 HAL pin will
        be created, if the ``minumum`` value is less than 0 then a s32 HAL pin will
        be created.
    """

    updatePreview = Signal(int)

    def __init__(self, parent=None):
        super(HalQColorSpinBox, self).__init__(parent)

        self._value_pin = None
        self._enabled_pin = None

        self._signed_int = True

        # self.valueChanged.disconnect()

        self.setMinimum(1)
        self.setMaximum(16777215)
        self.setDisplayIntegerBase(16)
        self.setPrefix("#")
        # self.valueChanged.connect(self.onValueChanged)

    def changeEvent(self, event):
        super(HalQColorSpinBox, self).changeEvent(event)
        if event == QEvent.EnabledChange and self._enabled_pin is not None:
            self._enabled_pin.value = self.isEnabled()

    def onValueChanged(self, value):
        if self._value_pin is not None:
            self._value_pin.value = value
            self.updatePreview.emit(value)

    def initialize(self):
        comp = hal.getComponent()
        obj_name = self.getPinBaseName()
        
        pin_typ = 's32' if self.minimum() < 0 else 'u32'

        # add spinbox.enable HAL pin
        self._enabled_pin = comp.addPin(f"{obj_name}.enable", "bit", "in")
        self._enabled_pin.value = self.isEnabled()
        self._enabled_pin.valueChanged.connect(self.setEnabled)
        
        # add spinbox.in HAL pin
        self._set_value_pin = comp.addPin(f"{obj_name}.in", pin_typ, "in")
        self._set_value_pin.valueChanged.connect(self.setValue)
        # self._set_value_pin.valueChanged.connect(self.onValueChanged)

        # add spinbox.out HAL pin
        self._value_pin = comp.addPin(f"{obj_name}.out", pin_typ, "out")
        self._value_pin.value = self._set_value_pin.value
        # self._value_pin.value = self.value()

        self.valueChanged.connect(self.onValueChanged)


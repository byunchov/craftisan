
from qtpy.QtWidgets import QSpinBox
from qtpy.QtCore import QEvent, Slot

from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget


class HalQSpinbox(QSpinBox, HALWidget):
    """HAL SpinBox

    SpinBox for displaying and setting `u32` and `s32` HAL pin values.

    .. table:: Generated HAL Pins

        ========================= ========= =========
        HAL Pin Name              Type      Direction
        ========================= ========= =========
        qtpyvcp.spinbox.enable    s32 | u32 in
        qtpyvcp.spinbox.in        s32 | u32 in
        qtpyvcp.spinbox.out       s32 | u32 out
        qtpyvcp.spinbox.io        s32 | u32 io
        ========================= ========= =========

    Note:
        If the ``minimum`` value property is set to 0 or greater a u32 HAL pin will
        be created, if the ``minumum`` value is less than 0 then a s32 HAL pin will
        be created.
    """
    def __init__(self, parent=None):
        super(HalQSpinbox, self).__init__(parent)

        self._value_pin = None
        self._enabled_pin = None
        self._io_pin =  None
        self._signed_int = True

        self.valueChanged.connect(self.onValueChanged)
    
    @Slot()
    def zero(self):
        self.setValue(0)

    def changeEvent(self, event):
        super(HalQSpinbox, self).changeEvent(event)
        if event == QEvent.EnabledChange and self._enabled_pin is not None:
            self._enabled_pin.value = self.isEnabled()

    def onValueChanged(self, value):
        if self._value_pin is not None:
            self._value_pin.value = value

        if self._io_pin is not None:
            self.blockSignals(True)
            self._io_pin.value = value
            self.blockSignals(False)

    def initialize(self):
        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

        if self.minimum() < 0:
            pin_typ = 's32'
        else:
            pin_typ = 'u32'

        # add spinbox.enable HAL pin
        self._enabled_pin = comp.addPin(f"{obj_name}.enable", "bit", "in")
        self._enabled_pin.value = self.isEnabled()
        self._enabled_pin.valueChanged.connect(self.setEnabled)

        # add spinbox.out HAL pin
        self._value_pin = comp.addPin(f"{obj_name}.out", pin_typ, "out")
        self._value_pin.value = self.value()

        # add spinbox.in HAL pin
        self._set_value_pin = comp.addPin(f"{obj_name}.in", pin_typ, "in")
        self._set_value_pin.valueChanged.connect(self.setValue)

        # add button.activated HAL pin
        self._io_pin = comp.addPin(f"{obj_name}.io", pin_typ, "io")
        self._io_pin.value = self.value()
        self._io_pin.valueChanged.connect(self.setValue)

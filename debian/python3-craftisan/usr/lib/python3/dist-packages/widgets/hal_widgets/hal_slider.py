from qtpy.QtWidgets import QSlider
from qtpy.QtCore import QEvent, Signal

from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget


class HalQSlider(QSlider, HALWidget):
    """HAL QSlider

    Slider for setting `u32` or `float` HAL pin values.

    .. table:: Generated HAL Pins

        ========================= ===== =========
        HAL Pin Name              Type  Direction
        ========================= ===== =========
        qtpyvcp.slider.enable     bit   in
        qtpyvcp.slider.out-i      u32   out
        qtpyvcp.slider.out-f      float out
        qtpyvcp.slider.in-i       u32   in
        qtpyvcp.slider.in-f       float in
        ========================= ===== =========

    Note:
        If the ``minimum`` value property is set to 0 or greater a u32 HAL pin will
        be created, if the ``minumum`` value is less than 0 then a s32 HAL pin will
        be created.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._enable_pin = None
        self._s32_value_pin = None
        self._float_value_pin = None
        self._set_int_value_pin = None
        self._set_float_value_pin = None

        self._signed_int = True
        # self.valueChanged.disconnect()

        # self.valueChanged.connect(self.onValueChanged)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event == QEvent.EnabledChange and self._enabled_pin is not None:
            self._enabled_pin.value = self.isEnabled()

    def onValueChanged(self, val):
        if self._s32_value_pin is not None:
            self._s32_value_pin.value = val
            self._float_value_pin.value = val / 100.0

    def initialize(self):
        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

        # add slider.enable HAL pin
        self._enabled_pin = comp.addPin(f"{obj_name}.enable", "bit", "in")
        self._enabled_pin.value = self.isEnabled()
        self._enabled_pin.valueChanged.connect(self.setEnabled)
        
        # add slider.in HAL pin
        self._set_int_value_pin = comp.addPin(f"{obj_name}.in-i", 'u32', "in")
        self._set_int_value_pin.valueChanged.connect(self.setValue)

        # add slider.in HAL pin
        self._set_float_value_pin = comp.addPin(f"{obj_name}.in-f", "float", "in")
        self._set_float_value_pin.valueChanged.connect(lambda x: self.setValue(int(x*100)))

        # add slider.percent HAL pin
        self._s32_value_pin = comp.addPin(f"{obj_name}.out-i", "u32", "out")
        self._s32_value_pin.value = self._set_int_value_pin.value

        # add slider.scale HAL pin
        self._float_value_pin = comp.addPin(f"{obj_name}.out-f", "float", "out")
        self._float_value_pin.value = self._set_float_value_pin.value
        # self._float_value_pin.value = self.value() / 100.0

        self.valueChanged.connect(self.onValueChanged)

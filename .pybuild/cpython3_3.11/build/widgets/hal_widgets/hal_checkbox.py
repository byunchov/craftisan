from qtpy.QtWidgets import QCheckBox
from qtpy.QtCore import QEvent

from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget


class HalQCheckBox(QCheckBox, HALWidget):
    """HAL CheckBox

    CheckBox for displaying and setting `bit` HAL pin values.

    .. table:: Generated HAL Pins

        ========================= ===== =========
        HAL Pin Name              Type  Direction
        ========================= ===== =========
        qtpyvcp.checkbox.enable   bit   in
        qtpyvcp.checkbox.check    bit   in
        qtpyvcp.checkbox.check-i  u32   in
        qtpyvcp.checkbox.checked  bit   out
        ========================= ===== =========
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self._enable_pin = None
        self._check_pin = None
        self._checked_pin = None
        self._checked_int_pin = None

        self.toggled.connect(self.onCheckedStateChanged)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event == QEvent.EnabledChange and self._enable_pin is not None:
            self._enable_pin.value = self.isEnabled()

    def onCheckedStateChanged(self, checked: bool):
        if self._checked_pin is not None:
            self._checked_pin.value = checked
            self._checked_int_pin.value = int(checked)

    def _checkFromInt(self, value: int):
        self.setChecked(bool(value))

    def initialize(self):
        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

        # add checkbox.enable HAL pin
        self._enable_pin = comp.addPin(f"{obj_name}.enable", "bit", "in")
        self._enable_pin.value = self.isEnabled()
        self._enable_pin.valueChanged.connect(self.setEnabled)

        # add checkbox.check HAL pin
        self._check_pin = comp.addPin(f"{obj_name}.check", "bit", "in")
        self._check_pin.valueChanged.connect(self.setChecked)

        self._check_pin_int = comp.addPin(f"{obj_name}.check-i", "u32", "in")
        self._check_pin_int.valueChanged.connect(self._checkFromInt)

        # add checkbox.checked HAL pin
        self._checked_pin = comp.addPin(f"{obj_name}.checked", "bit", "out")
        self._checked_pin.value = self._check_pin.value or bool(self._check_pin_int.value)

        # add checkbox.checked HAL pin
        self._checked_int_pin = comp.addPin(f"{obj_name}.checked-i", "u32", "out")
        self._checked_int_pin.value = int(self._check_pin.value or self._check_pin_int.value)


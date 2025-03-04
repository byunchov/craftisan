from qtpy.QtWidgets import QCheckBox
from qtpy.QtCore import Property, QEvent

from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget
from qtpyvcp.widgets.input_widgets.setting_slider import VCPAbstractSettingsWidget
from qtpyvcp import SETTINGS

class HalSettingsCheckBox(QCheckBox, HALWidget, VCPAbstractSettingsWidget):
    """HAL CheckBox

    CheckBox for displaying and setting `bit` HAL pin values.

    .. table:: Generated HAL Pins

        ========================= ===== =========
        HAL Pin Name              Type  Direction
        ========================= ===== =========
        qtpyvcp.checkbox.enable   bit   in
        qtpyvcp.checkbox.check    bit   in
        qtpyvcp.checkbox.checked  bit   out
        ========================= ===== =========
    """

    DEFAULT_RULE_PROPERTY = 'Enable'
    RULE_PROPERTIES = VCPAbstractSettingsWidget.RULE_PROPERTIES.copy()
    RULE_PROPERTIES.update({
        'Checked': ['setChecked', bool],
    })

    def __init__(self, parent=None):
        super(HalSettingsCheckBox, self).__init__(parent)

        self._enable_pin = None
        self._check_pin = None
        self._checked_pin = None

        self.toggled.connect(self.onCheckedStateChanged)

    def setDisplayChecked(self, checked):
        self.blockSignals(True)
        self.setChecked(checked)
        # self._checked_pin.value = checked
        self.blockSignals(False)

    def changeEvent(self, event):
        super(HalSettingsCheckBox, self).changeEvent(event)
        if event == QEvent.EnabledChange and self._enable_pin is not None:
            self._enable_pin.value = self.isEnabled()

    def onCheckedStateChanged(self, checked):
        if self._checked_pin is not None:
            self._checked_pin.value = checked

        if self._setting is not None:
            self._setting.setValue(checked)

    def initialize(self):
        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

        self._setting = SETTINGS.get(self._setting_name)
        if self._setting is not None:

            value = self._setting.getValue()

            self.setDisplayChecked(value)
            self.toggled.emit(value)
            self._setting.notify(self.setDisplayChecked)

        # add checkbox.enable HAL pin
        self._enable_pin = comp.addPin(f"{obj_name}.enable", "bit", "in")
        self._enable_pin.value = self.isEnabled()
        self._enable_pin.valueChanged.connect(self.setEnabled)

        # add checkbox.check HAL pin
        self._check_pin = comp.addPin(f"{obj_name}.check", "bit", "in")
        self._check_pin.value = self.isChecked()
        self._check_pin.valueChanged.connect(self.setChecked)

        # add checkbox.checked HAL pin
        self._checked_pin = comp.addPin(f"{obj_name}.checked", "bit", "out")
        self._checked_pin.value = self.isChecked()

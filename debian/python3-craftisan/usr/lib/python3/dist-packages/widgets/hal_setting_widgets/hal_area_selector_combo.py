from qtpy.QtWidgets import QComboBox
from qtpy.QtCore import Qt, Property, QEvent

from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget
from qtpyvcp.widgets.input_widgets.setting_slider import VCPAbstractSettingsWidget
from qtpyvcp import SETTINGS

class HalAreaSelectorComboBox(QComboBox, HALWidget, VCPAbstractSettingsWidget):
    """HAL QComboBox

    QComboBox for displaying and setting area code using `u32` HAL pin values.

    .. table:: Generated HAL Pins

        ========================== ===== =========
        HAL Pin Name               Type  Direction
        ========================== ===== =========
        qtpyvcp.combobox.enable    bit   in
        qtpyvcp.combobox.area-code bit   out
        ========================== ===== =========
    """

    DEFAULT_RULE_PROPERTY = 'Enable'

    AreaCodeRole = 102

    def __init__(self, parent=None):
        super(HalAreaSelectorComboBox, self).__init__(parent)

        self._enable_pin = None
        self._area_code = None

        self._area_options = None

        self.currentIndexChanged.connect(self.onIndexChanged)

    def setDisplayId(self, area_id):
        self.blockSignals(True)
        index = self.indexFromAreaId(area_id)
        self.setCurrentIndex(index)
        self.blockSignals(False)
    
    def setDisplayIndex(self, index):
        self.blockSignals(True)
        self.setCurrentIndex(index)
        self.blockSignals(False)

    def indexFromAreaId(self, area_id):
        try:
            keys = tuple(self._area_options.values())
            return keys.index(area_id)
        except ValueError:
            return 0

    def changeEvent(self, event):
        super(HalAreaSelectorComboBox, self).changeEvent(event)
        if event == QEvent.EnabledChange and self._enable_pin is not None:
            self._enable_pin.value = self.isEnabled()

    def onIndexChanged(self, index):
        area_code = self.currentData(Qt.UserRole)
        if self._area_code is not None:    
            self._area_code.value = area_code

        if self._setting is not None:
            self._setting.setValue(area_code)

    def initialize(self):
        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

        self._setting = SETTINGS.get(self._setting_name)
        if self._setting is not None:

            value = self._setting.getValue()

            self._area_options = self._setting.dict_options or {10: "Left Area"}
            if isinstance(self._area_options, dict):
                for area_name, area_code in self._area_options.items():
                    if isinstance(area_name, str):
                        self.addItem(area_name, area_code)
                    elif isinstance(area_name, int):
                        self.addItem(area_code, area_name)

            current_index = self.indexFromAreaId(value)
            self.setDisplayIndex(current_index)
            self.currentIndexChanged.emit(current_index)

            # self._setting.notify(self.setDisplayId)

        # add checkbox.enable HAL pin
        self._enable_pin = comp.addPin(f"{obj_name}.enable", "bit", "in")
        self._enable_pin.value = self.isEnabled()
        self._enable_pin.valueChanged.connect(self.setEnabled)

        # add checkbox.checked HAL pin
        self._area_code = comp.addPin(f"{obj_name}.area-code", "u32", "out")
        self._area_code.value = self.currentData(Qt.UserRole)


from qtpyvcp.widgets.qtdesigner import _DesignerPlugin
from widgets.hal_widgets import *
from widgets.hal_setting_widgets import HalSettingsCheckBox, HalAreaSelectorComboBox
from widgets.misc import QFilePathLineEdit, QFileSystemTable, QFileLineEdit

from widgets.tool_changer.tool_table import ToolChangerTableView
from widgets.laser_pos.laserpos_view import LaserPositionTable


class ToolChangerTable_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return ToolChangerTableView


class LaserPositionTable_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return LaserPositionTable


class HalColorSpinBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return HalQColorSpinBox


class HalColorPreview_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return QColorPreview
    

class HalColorPickerButton_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return QColorPickerButton


class HalSettingsCheckBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return HalSettingsCheckBox


class HalAreaSelectorComboBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return HalAreaSelectorComboBox


class QFilePathLineEdit_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return QFilePathLineEdit


class QFileLineEdit_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return QFileLineEdit
    

class QFileSystemTable_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return QFileSystemTable


class HalQSlider_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return HalQSlider
    

class HalQCheckBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return HalQCheckBox
    
class HalQButton_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return HalQButton
    
class HalQSpinbox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return HalQSpinbox
    
class HalQDoubleSpinBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return HalQDoubleSpinBox
from qtpy.QtCore import Slot, Qt
from qtpy.QtGui import QFontDatabase
from qtpy.QtWidgets import QAbstractButton, QApplication

from qtpyvcp.utilities import logger
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow

import craftisan_rc

LOG = logger.getLogger(f'qtpyvcp.{__name__}')

class CraftisanWindow(VCPMainWindow):
    """Main window class for the VCP."""
    def __init__(self, *args, **kwargs):
        super(CraftisanWindow, self).__init__(*args, **kwargs)
        self.filesystem_table.sortByColumn(0, Qt.AscendingOrder) # sorting via 'datemodified' header 3
        # self.filesystem_table.sortByColumn(3, Qt.DescendingOrder) # sorting via 'datemodified' header 3
        # self.run_from_line_Num.setValidator(QRegExpValidator(QRegExp("[0-9]*")))
        QApplication.setStyle('Fusion')

    @Slot(QAbstractButton)
    def on_sidebartabGroup_buttonClicked(self, button):
        self.sidebar_widget.setCurrentIndex(button.property('page'))

    @Slot(QAbstractButton)
    def on_gcodemdibtnGroup_buttonClicked(self, button):
        self.gcode_mdi.setCurrentIndex(button.property('page'))

    def on_set_wco_offset_Btn_clicked(self):
        if self.set_wco_offset_Btn.isChecked():
            self.wco_rotation.setText('1')
        else:
            self.wco_rotation.setText('0')

    @Slot(QAbstractButton)
    def on_fileviewerbtnGroup_buttonClicked(self, button):
        self.file_viewer_widget.setCurrentIndex(button.property('page'))


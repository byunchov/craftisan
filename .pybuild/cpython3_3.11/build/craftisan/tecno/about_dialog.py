from craftisan.ui.about_tecno_ui import Ui_Dialog
from PyQt5.QtWidgets import QDialog

class AboutTecnoDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
  
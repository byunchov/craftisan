import os
from qtpy.QtWidgets import QLineEdit
from qtpy.QtCore import Signal, Slot, Property, QTimer


ALLOWED_EXT = ('.ngc', '.lpos', '.txt')

class QFileLineEdit(QLineEdit):
    loadFile = Signal(str)

    def __init__(self, parent=None):
        super(QFileLineEdit, self).__init__(parent)
        self._debounce_time = 400
        self._path = ''

        self.debounce = QTimer(self)
        self.debounce.setInterval(self._debounce_time)
        self.debounce.setSingleShot(True)
        self.debounce.timeout.connect(self.fetchFilePath)
        self.textEdited.connect(self.debounce.start)

    def fetchFilePath(self):
        path: str = self.text()

        if not os.path.exists(path):
            return
        
        if os.path.isfile(path):
            if path.endswith(ALLOWED_EXT):
                self.loadFile.emit(path)
            self._path = path

    @Property(int)
    def debounceTime(self):
        return self._debounce_time

    @debounceTime.setter
    def debounceTime(self, duration):
        self._debounce_time = duration
        self.debounce.setInterval(duration)

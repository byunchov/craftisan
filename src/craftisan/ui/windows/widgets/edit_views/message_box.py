from PyQt5.QtWidgets import QMessageBox, QWidget

def confirmAction(parent: QWidget, message: str, title: str=None) -> bool:
    box = QMessageBox.warning(parent,
                    'Confirm' if title is None else title,
                    message,
                    QMessageBox.Yes,
                    QMessageBox.No)

    return box == QMessageBox.Yes
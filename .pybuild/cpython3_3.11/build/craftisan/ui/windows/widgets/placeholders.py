from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap


class PlaceholderWidget(QWidget):
    def __init__(self, text = None, image = None, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.widget_lauyout = QVBoxLayout(self)
        self.setStyleSheet("""
            
            QLabel{
                font-size: 35px;
                font-weight: bold;
            }
        """)

        self.p_label = QLabel(text or 'No tool selected', self)
        self.p_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.p_icon = QLabel(self)
        self.p_icon.setFixedSize(QSize(256, 256))
        self.p_icon.setScaledContents(True)
        self.p_icon.setPixmap(QPixmap(image or ':/images/icons/select_click.svg'))
        # self.p_icon.setPixmap(QPixmap(image or ':/images/dbms/selection_tool.png'))

        self.widget_lauyout.addStretch()
        self.widget_lauyout.addWidget(self.p_icon)
        self.widget_lauyout.addWidget(self.p_label)
        self.widget_lauyout.addStretch()

        self.widget_lauyout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.widget_lauyout)

    def set_icon(self, icon_path: str):
        self.p_icon.setPixmap(QPixmap(icon_path))
    
    def set_text(self, text: str):
        self.p_label.setText(text)
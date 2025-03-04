import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea
from craftisan.ui.windows.widgets.edit_views import BaseEditWidget, SingleTipDataWidget

import craftisan.craftisan_rc

class PlaceholderWidget(QWidget):
    def __init__(self, text = None, image = None, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.widget_lauyout = QVBoxLayout(self)
        self.setStyleSheet("""
            PlaceholderWidget{
                background: red;
            }
            
            QLabel{
                font-size: 35px;
                font-weight: bold;
            }
        """)

        self.p_label = QLabel(text or 'No tool selected', self)

        self.widget_lauyout.addStretch()
        self.widget_lauyout.addWidget(self.p_label)
        self.widget_lauyout.addStretch()

        self.widget_lauyout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.widget_lauyout)


class MainForm(QWidget):
    def __init__(self):
        super(MainForm, self).__init__()
        self.initUI()

    def initUI(self):
        self._scrollArea = QScrollArea()
        self.setWindowTitle('Form Switcher')
        self.setGeometry(100, 100, 400, 200)

        self.stackedWidget = QStackedWidget()
        self.form1 = SingleTipDataWidget()
        self.form2 = PlaceholderWidget()
        # self.form2 = QPlainTextEdit()
        self.btn1 = QPushButton('First')
        self.btn2 = QPushButton('Second')

        self.stackedWidget.addWidget(self.form1)
        self.stackedWidget.addWidget(self.form2)

        self._layout = QVBoxLayout()
        # self._layout.addWidget(self.stackedWidget)

        self._scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scrollArea.setWidgetResizable(True)
        self._scrollArea.setWidget(self.stackedWidget)

        self._layout.addWidget(self._scrollArea)
        self._layout.addWidget(self.btn1)
        self._layout.addWidget(self.btn2)
        self.setLayout(self._layout)

        self.btn1.clicked.connect(self.first)
        self.btn2.clicked.connect(self.second)

        self.setStyleSheet("""
MainForm, PlaceholderWidget, SingleTipDataWidget{
    background: #7f9dc2;
}

QScrollArea
                           {
    border: 3px solid #425a76;
    border-radius: 6px;
    background-color: transparent;
}
QStackedWidget{
    background-color: transparent;
}
""")

    def first(self):
        # self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget.removeWidget(self.form1)
        # self.form = PlaceholderWidget()
        # self.stackedWidget.addWidget(self.form1)
        count = self.stackedWidget.count()
        print(f"{count=}")

    def second(self):
        # self.stackedWidget.removeWidget(self.form1)
        self.form1 = SingleTipDataWidget()
        self.stackedWidget.addWidget(self.form1)
        count = self.stackedWidget.count()
        self.stackedWidget.setCurrentIndex(count - 1)
        print(f"{count=}")


if __name__ == '__main__':
    style_file = '/home/cnc/Public/craftisan/src/craftisan/styles/craftisan.qss'

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    with open(style_file, 'r') as f:
        app.setStyleSheet(f.read())

    window = MainForm()
    window.setGeometry(10, 100, 350, 600)
    window.show()
    sys.exit(app.exec_())
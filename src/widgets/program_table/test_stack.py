import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea
from widgets.tool_db_manager.tool_edit_views.base_view import BaseEditWidget
from widgets.tool_db_manager.tool_edit_views.single_tip_data import SingleTipDataWidget

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
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainForm()
    window.setGeometry(10, 100, 350, 600)
    window.show()
    sys.exit(app.exec_())
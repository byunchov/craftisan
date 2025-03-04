from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtGui import QPixmap
from craftisan.tool_db.model import Tool
from craftisan.utilities.misc import SUBCAT_TAGS

DEFAULT_HELP_IMAGE = ':/images/dbms/help/cutters_routers.jpg'
HELP_IMAGE_PATH = ':/images/dbms/help/{tag}.jpg'


class ToolHelpWidget(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.toolId = -1
        self.helpImgSquare = 256
        self.toolIconSquare = 96

        self._initUI()

    def _initUI(self):
        self.widget_lauyout = QVBoxLayout(self)
        self.setStyleSheet("""
            QLabel[role="imgFrame"]{
                border-radius: 5px;
                border: 3px solid #425a76;
                background: transparent;
            }
        """)

        # Help image
        self.helpImage = QLabel()
        self.helpImage.setProperty('role', 'imgFrame')
        self.helpImage.setFixedSize(*(self.helpImgSquare,)*2)
        self.helpImage.setScaledContents(True)

        # Tool icon 
        tool_icon_frame = QWidget(self)
        tool_display_layout = QHBoxLayout()
        self.toolIcon = QLabel()
        self.toolIcon.setProperty('role', 'imgFrame')
        self.toolIcon.setFixedSize(QSize(*(self.toolIconSquare,)*2))
        self.toolIcon.setScaledContents(True)


        tool_display_layout.addWidget(self.toolIcon)
        tool_icon_frame.setLayout(tool_display_layout)

        self.widget_lauyout.addWidget(self.helpImage)
        self.widget_lauyout.addWidget(tool_icon_frame)
        self.widget_lauyout.addStretch()

        self._clearHelp()

        self.setLayout(self.widget_lauyout)

    @pyqtSlot(Tool)
    def updateHelp(self, tool: Tool):
        if tool is None:
            if self.toolId > 0:
                self._clearHelp()
                self.toolId = -1
            return
        tag = SUBCAT_TAGS.get(tool.subCategoryId, SUBCAT_TAGS[3])
        helpImage = QPixmap(HELP_IMAGE_PATH.format(tag=tag))
        self.helpImage.setPixmap(helpImage)

        self.toolId = tool.id

        if tool.icon:
            toolIcon = QPixmap(tool.icon)
            self.toolIcon.setPixmap(toolIcon)
            self.toolIcon.show()

    def _clearHelp(self):
        self.helpImage.setPixmap(QPixmap())
        self.toolIcon.setPixmap(QPixmap())
        self.toolIcon.hide()

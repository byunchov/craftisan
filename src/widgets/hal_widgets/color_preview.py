from qtpy.QtWidgets import QWidget
from qtpy.QtCore import Slot, Property
from PyQt5.QtGui import QColor, QPainter, QPen


class QColorPreview(QWidget):
    def __init__(self, parent=None, color = None):
        super().__init__(parent)

        self.current_color = color or QColor(0)
        self._icon_size = 28
        self.setFixedSize(self._icon_size, self._icon_size)
        # shadow_effect = QGraphicsDropShadowEffect(offset=QPointF(4, 4), blurRadius=5)
        # self.setGraphicsEffect(shadow_effect)

    @Slot(QColor)
    def updatePreviewColor(self, color: QColor):
        self.current_color = color
        self.update()

    @Slot(int)
    def updatePreviewColor(self, color: int):
        self.current_color = QColor(color)
        self.update()

    @Property(int)
    def previewRectSize(self):
        if self._icon_size is None:
            return 28
        return self._icon_size

    @previewRectSize.setter
    def previewRectSize(self, size):
        self._icon_size = size
        self.setFixedSize(self._icon_size, self._icon_size)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Draw sunken border
        border_color = self.palette().color(self.backgroundRole()).darker(180)
        painter.setPen(QPen(border_color, 2.4))
        painter.drawRect(self.rect())

        # Fill with the current color
        painter.fillRect(self.rect().adjusted(1, 1, -1, -1), self.current_color)

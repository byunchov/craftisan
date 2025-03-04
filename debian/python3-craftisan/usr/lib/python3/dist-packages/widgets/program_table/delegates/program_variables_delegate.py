from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QItemDelegate, QSpinBox, QDoubleSpinBox

class CustomDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        dtype: str = index.data(Qt.UserRole)
        if dtype in ('b', 'bool'):
            return None
        elif dtype in ('i', 'int'):
            editor = QSpinBox(parent)
            # editor.setFrame(False)
            editor.setAlignment(Qt.AlignLeft)
            editor.setMinimum(-4000)
            editor.setMaximum(4000)
            editor.setStepType(QSpinBox.AdaptiveDecimalStepType)
            return editor
        elif dtype in ('f', 'float'):
            editor = QDoubleSpinBox(parent)
            # editor.setFrame(False)
            editor.setAlignment(Qt.AlignLeft)
            editor.setDecimals(4)
            editor.setRange(-4000, 4000)
            editor.setStepType(QSpinBox.AdaptiveDecimalStepType)
            return editor        
        
        return super().createEditor(parent, option, index)

    def paint(self, painter, option, index):
        if isinstance(index.data(), bool):
            self.drawCheck(painter, option, option.rect, Qt.Checked if bool(index.data()) else Qt.Unchecked)
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        if isinstance(index.data(), bool):
            event_type = event.type()

            is_mouse_click = isinstance(event, QMouseEvent) and \
                (event_type == event.MouseButtonRelease and event.button() == Qt.LeftButton)
            is_key_press = isinstance(event, QKeyEvent) and \
                (event_type == event.KeyPress and event.key() == Qt.Key_Space)

            if is_mouse_click or is_key_press:
                self.setModelData(None, model, index)
                return True
            return False
        
        return super().editorEvent(event, model, option, index)

    def setModelData(self, editor, model, index):
        if isinstance(index.data(), bool):
            model.setData(index, not bool(index.data()), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)
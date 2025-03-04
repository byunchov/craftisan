from PyQt5.QtWidgets import QFrame, QVBoxLayout, QAction, QScrollArea, QStackedWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThreadPool, Qt
from PyQt5.QtGui import QIcon
from craftisan.tecno.widgets.placeholders import PlaceholderWidget
from craftisan.utilities.worker import Worker
from craftisan.tecno.widgets.edit_views.message_box import confirmAction
from craftisan.tecno.widgets.edit_views import (
    BaseEditWidget, SingleTipDataWidget, MultiTipDataWidget, TiltingAggregateDataWidget, Horizontal12TipDataWidget, SawTipDataWidget)
from craftisan.tool_db.model import Tool
from sqlalchemy.orm import make_transient
from craftisan.tecno.widgets.managers import DB_CHANGES


class ToolEditWidget(QFrame):
    editorActive = pyqtSignal(bool)
    updateToolHelp = pyqtSignal(object)
    updateTreeView = pyqtSignal(object)
    addToolInTree = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor: BaseEditWidget = None
        # self.editorOld = None
        self.toolId = 0

        self.editorSwitch = {
            1: SingleTipDataWidget,
            2: SingleTipDataWidget,
            3: SingleTipDataWidget,
            4: SingleTipDataWidget,
            5: MultiTipDataWidget,
            6: TiltingAggregateDataWidget,
            7: Horizontal12TipDataWidget,
            8: SawTipDataWidget,
        }
        self._initUI()
        self._initActions()
        self._connectActions()
        self._connectSignals()
        self._emitSignals()

    def _initUI(self):
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)

        self.stackedWidget = QStackedWidget()
        self.placeholder = PlaceholderWidget()
        self.stackedWidget.addWidget(self.placeholder)

        self._layout = QVBoxLayout()

        self.scrollArea.setWidget(self.stackedWidget)
        self._layout.addWidget(self.scrollArea)
        self.setLayout(self._layout)
        # self.setProperty('role', 'floating')

    def _fetchTool(self, toolId: int, callback=None):
        worker = Worker(DB_CHANGES.getToolById, toolId)
        pool = QThreadPool.globalInstance()
        if callback is not None:
            worker.signals.result.connect(callback)
        else:
            worker.signals.result.connect(self.displayData)
        pool.start(worker)

    def _initActions(self):
        self.apply_changes_action = QAction(
            QIcon(':/images/dbms/apply.png'), "Apply Changes")
        self.discard_changes_action = QAction(
            QIcon(':/images/dbms/discard.png'), "Discard Changes")

        self.apply_changes_action.setShortcut("Ctrl+Return")
        self.discard_changes_action.setShortcut("Ctrl+0")

    def _connectActions(self):
        self.apply_changes_action.triggered.connect(self.saveTool)
        self.discard_changes_action.triggered.connect(self.discardTool)

    def _connectSignals(self):
        self.editorActive.connect(self._enableActions)

    def _emitSignals(self):
        self.editorActive.emit(False)

    @pyqtSlot(dict)
    def previewTool(self, toolNode: dict):
        if toolNode['nodeType'] != 'tool':
            if self.editor is not None:
                self.stackedWidget.removeWidget(self.editor)
                self.editor = None
                self.toolId = 0
                self.editorActive.emit(False)
                self.updateToolHelp.emit(None)
            return

        toolId = int(toolNode['id'])
        if self.toolId != toolId:
            self.toolId = toolId
            self._fetchTool(self.toolId, self._showEditor)

    @pyqtSlot(Tool)
    def addTool(self, tool: Tool):
        if tool is None:
            return

        self._addTool(tool)

    @pyqtSlot(int)
    def modifyTool(self, toolId: int):
        if toolId < 0:
            return

        self.toolId = toolId
        self._fetchTool(self.toolId, self._modifyTool)

    @pyqtSlot(int)
    def duplicateTool(self, toolId: int):
        if toolId < 0:
            return

        # print(f"duplicateTool() -> {toolId=}")

        self.toolId = toolId
        self._fetchTool(self.toolId, self._duplicateTool)

    def _addTool(self, tool: Tool):
        tool.id = DB_CHANGES.generateToolId(subcatId=tool.subCategoryId)
        self._showEditor(tool, readOnly=False)

    def _modifyTool(self, tool: Tool):
        self._showEditor(tool, readOnly=False)

    def _duplicateTool(self, tool: Tool):
        # print(f"_duplicateTool() -> {tool=}")

        if tool is None:
            return
        
        # newTool = Tool(tool.asdict())
        # newTool.id = DB_CHANGES.generateToolId(toolId=tool.id)
        # self._showEditor(newTool, readOnly=False)

        make_transient(tool)

        tool.id = DB_CHANGES.generateToolId(toolId=tool.id)
        self._showEditor(tool, readOnly=False)

    def _showEditor(self, tool: Tool, readOnly=True):
        if self.editor is not None:
            self.stackedWidget.removeWidget(self.editor)

        if tool is None:
            self.toolId = 0
            return

        self.editor = self.editorSwitch.get(tool.subCategoryId, 1)()

        if self.editor is None:
            return

        self.editor.fillToolData(tool)
        self.editorActive.emit(not readOnly)

        self.stackedWidget.addWidget(self.editor)
        count = self.stackedWidget.count()
        self.stackedWidget.setCurrentIndex(count - 1)

        self.updateToolHelp.emit(tool)

    def displayData(self, tool: Tool):
        if self.editor is not None:
            self.stackedWidget.removeWidget(self.editor)

        if tool is None:
            self.toolId = 0
            return

        self.editor = self.editorSwitch.get(tool.subCategoryId, 1)()

        if self.editor is None:
            return

        self.editor.fillToolData(tool)
        self.editor.setEnabled(False)

        self.stackedWidget.addWidget(self.editor)
        count = self.stackedWidget.count()
        self.stackedWidget.setCurrentIndex(count - 1)

        self.updateToolHelp.emit(tool)

    def saveTool(self, *args):
        isValid, tool = self.editor.validate()

        if isValid:
            DB_CHANGES.saveItem(tool)
            self.updateToolHelp.emit(tool)
            self.updateTreeView.emit(tool)
            self.addToolInTree.emit(tool)
            self.editorActive.emit(False)

    def discardTool(self, *args):
        if confirmAction(self, f"Are you sure you want to discard the changes?"):
            self._fetchTool(self.toolId)
            self.editorActive.emit(False)

    def _enableActions(self, enabled: bool = True):
        # self.stackedWidget.setEnabled(enabled)
        if self.editor is not None:
            self.editor.setEnabled(enabled)

        self.apply_changes_action.setEnabled(enabled)
        self.discard_changes_action.setEnabled(enabled)

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QMainWindow, QToolBar, QHBoxLayout, QAction
from craftisan.tecno.widgets import ToolEditWidget, ToolTreeView, ToolHelpWidget
from craftisan.tecno.widgets.edit_views.message_box import confirmAction
from craftisan.tecno.widgets.managers import DB_CHANGES
from craftisan.tecno.about_dialog import AboutTecnoDialog

WIN_TITLE = 'Craftisan TecnoDB'
WIN_ICON = ':/images/icons/icon_db.png'

class TecnoManagerWindow(QMainWindow):
    def __init__(self):
        super(TecnoManagerWindow, self).__init__()
        self.setWindowTitle(WIN_TITLE)
        self.setWindowIcon(QIcon(WIN_ICON))
        self.setGeometry(0, 0, 1915, 1011)
        
        self.toolTree = ToolTreeView(self)
        self.toolEditor = ToolEditWidget(self)
        self.toolHelp = ToolHelpWidget(self)

        self.central_widget = QWidget(self)
        # self.central_widget.setProperty('role', 'central')

        self.h_layout = QHBoxLayout(self.central_widget)
        self.h_layout.setAlignment(Qt.AlignCenter)
        self.h_layout.setContentsMargins(*(16,)*4)

        self.h_layout.addWidget(self.toolTree)
        self.h_layout.addWidget(self.toolHelp)
        self.h_layout.addWidget(self.toolEditor)

        self.setCentralWidget(self.central_widget)
        self._initActions()
        self._createMenuBar()
        self._createTreeToolBar()
        self._createEditorToolBar()
        self._connectSignals()
        self._connectActions()
        self._enableEditActions(all_actions=False)
        self._enableFileActions(save=False, reload_lcnc=True, reload_tree=True)

    def _initActions(self):
        self.exitAction = QAction("&Exit")
        self.helpContentAction = QAction("&Help content")
        self.aboutAction = QAction("&About")

        self.exitAction.setShortcut("Ctrl+Q")
    
    def _createMenuBar(self):
        menuBar = self.menuBar()
        # File menu
        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(self.toolTree.save_db_action)
        fileMenu.addAction(self.toolTree.reload_tree_action)
        fileMenu.addAction(self.toolTree.reload_lcnc_action)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)
        # Edit menu
        editMenu = menuBar.addMenu("&Edit")
        editMenu.addAction(self.toolTree.add_tool_action)
        editMenu.addAction(self.toolTree.modify_tool_action)
        editMenu.addAction(self.toolTree.delete_tool_action)
        # Help menu
        helpMenu = menuBar.addMenu("&Help")
        # helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)

    def _createTreeToolBar(self):
        icon_size = QSize(48, 48)
        # File toolbar
        treeToolBar = QToolBar("Tool DB Actions", self)
        treeToolBar.setIconSize(icon_size)
        treeToolBar.setMovable(False)
        treeToolBar.addAction(self.toolTree.save_db_action)
        treeToolBar.addAction(self.toolTree.reload_tree_action)
        treeToolBar.addAction(self.toolTree.reload_lcnc_action)
        treeToolBar.addSeparator()
        treeToolBar.addAction(self.toolTree.add_tool_action)
        treeToolBar.addAction(self.toolTree.modify_tool_action)
        treeToolBar.addAction(self.toolTree.delete_tool_action)
        treeToolBar.addSeparator()
        treeToolBar.addAction(self.toolTree.duplicate_tool_action)
        treeToolBar.setProperty('position', 'top')

        self.addToolBar(Qt.TopToolBarArea, treeToolBar)

    def _createEditorToolBar(self):
        icon_size = QSize(42, 42)

        editorToolbar = QToolBar("Tool Editor Actions", self)
        editorToolbar.setIconSize(icon_size)
        editorToolbar.setMovable(False)
        editorToolbar.addAction(self.toolEditor.apply_changes_action)
        editorToolbar.addAction(self.toolEditor.discard_changes_action)
        editorToolbar.setProperty('position', 'right')

        self.addToolBar(Qt.RightToolBarArea, editorToolbar)

    def _connectSignals(self):
        self.toolTree.insertTool.connect(self.toolEditor.addTool)
        self.toolTree.modifyTool.connect(self.toolEditor.modifyTool)
        self.toolTree.duplicateTool.connect(self.toolEditor.duplicateTool)
        self.toolTree.changePreview.connect(self.toolEditor.previewTool)
        self.toolTree.changePreview.connect(self.onTreeSelectionChange)

        self.toolEditor.editorActive.connect(self.onEditorActive)
        self.toolEditor.addToolInTree.connect(self.toolTree.addTool)
        self.toolEditor.updateToolHelp.connect(self.toolHelp.updateHelp)
        self.toolEditor.updateTreeView.connect(self.toolTree.updateTool)

    def _connectActions(self):
        self.exitAction.triggered.connect(self.onExitAction)
        self.helpContentAction.triggered.connect(self.onHelpContentAction)
        self.aboutAction.triggered.connect(self.onAboutAction)

    def _enableEditActions(self, *, add=False, modify=False, delete=False, duplicate=False, all_actions=None):
        multi_args = all_actions is not None
        self.toolTree.add_tool_action.setEnabled(add if not multi_args else all_actions)
        self.toolTree.modify_tool_action.setEnabled(modify if not multi_args else all_actions)
        self.toolTree.delete_tool_action.setEnabled(delete if not multi_args else all_actions)
        self.toolTree.duplicate_tool_action.setEnabled(duplicate if not multi_args else all_actions)

    def _enableFileActions(self, save=False, reload_tree=False, reload_lcnc=False, all_actions=None):
        multi_args = all_actions is not None
        self.toolTree.save_db_action.setEnabled((save if not multi_args else all_actions) and DB_CHANGES.isNotEmpty())
        self.toolTree.reload_tree_action.setEnabled(reload_tree if not multi_args else all_actions)
        self.toolTree.reload_lcnc_action.setEnabled(reload_lcnc if not multi_args else all_actions)

    def onTreeSelectionChange(self, itemData: dict):
        nodeType = itemData.get('nodeType', None)

        if nodeType is None:
            return
        
        if nodeType == 'category':            
            self._enableEditActions(all_actions=False)
        elif nodeType == 'subcategory':
            self._enableEditActions(add=True)
        elif nodeType == 'tool':
            self._enableEditActions(all_actions=True)

    def onEditorActive(self, active):
        self._enableEditActions(all_actions=not active)
        self._enableFileActions(all_actions=not active)
        self.toolTree.setEnabled(not active)

    def onExitAction(self, *args):
        self.close()

    def onHelpContentAction(self, *args):
        pass

    def onAboutAction(self, *args):
        aboutDialog = AboutTecnoDialog(self)
        aboutDialog.exec_()

    def closeEvent(self, event):
        if DB_CHANGES.isNotEmpty():                
            reply = confirmAction(self, 'There are unsaved changes? Do you wish to save them?', 'Unsaved changes')

            if reply:
                DB_CHANGES.commitChanges()

        event.accept()

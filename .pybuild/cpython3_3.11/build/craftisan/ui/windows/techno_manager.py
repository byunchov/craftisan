#!/usr/bin/env python3

import sys
import time
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QToolBar, QHBoxLayout, QSplashScreen, QAction
from craftisan.ui.windows.widgets import ToolEditWidget, ToolTreeView, ToolHelpWidget
from craftisan.ui.windows.widgets.edit_views.message_box import confirmAction
from craftisan.ui.windows.widgets.managers import DB_CHANGES

import craftisan.craftisan_rc


class TecnoManagerWindow(QMainWindow):
    def __init__(self):
        super(TecnoManagerWindow, self).__init__()
        self.setWindowIcon(QIcon(':/images/icons/icon_db.png'))
        
        self.toolTree = ToolTreeView(self)
        self.toolEditor = ToolEditWidget(self)
        self.toolHelp = ToolHelpWidget(self)

        self.central_widget = QWidget(self)
        self.central_widget.setProperty('role', 'central')

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
        self._enableEditActions(False)
        self._enableTreeActions(False)

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
        helpMenu.addAction(self.helpContentAction)
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

        self.toolEditor.editorActive.connect(self.onEditorActive)
        self.toolEditor.addToolInTree.connect(self.toolTree.addTool)
        self.toolEditor.updateToolHelp.connect(self.toolHelp.updateHelp)
        self.toolEditor.updateTreeView.connect(self.toolTree.updateTool)

    def _connectActions(self):
        self.exitAction.triggered.connect(self.onExitAction)
        self.helpContentAction.triggered.connect(self.onHelpContentAction)
        self.aboutAction.triggered.connect(self.onAboutAction)

    def _enableEditActions(self, enabled):
        self.toolTree.modify_tool_action.setEnabled(enabled)
        self.toolTree.delete_tool_action.setEnabled(enabled)
        self.toolTree.duplicate_tool_action.setEnabled(enabled)
        # self.tree.add_tool_action.setEnabled(not enabled)

    def _enableTreeActions(self, enabled):
        # if not enabled:
        #     # self.toolTree.save_db_action.setEnabled(enabled)
        #     self.toolTree.add_tool_action.setEnabled(enabled)
        
        self.toolTree.add_tool_action.setEnabled(enabled)
        self.toolTree.save_db_action.setEnabled(enabled)
        self.toolTree.reload_tree_action.setEnabled(enabled)
        self.toolTree.reload_lcnc_action.setEnabled(enabled)        
        self.toolTree.modify_tool_action.setEnabled(enabled)
        self.toolTree.delete_tool_action.setEnabled(enabled)
        self.toolTree.duplicate_tool_action.setEnabled(enabled)

    def onEditorActive(self, active):
        self._enableEditActions(active)
        self._enableTreeActions(not active)
        self.toolTree.setEnabled(not active)

    def onExitAction(self, *args):
        self.close()

    def onHelpContentAction(self, *args):
        pass

    def onAboutAction(self, *args):
        pass

    def closeEvent(self, event):
        if DB_CHANGES.isNotEmpty():                
            reply = confirmAction(self, 'There are unsaved changes? Do you wish to save them?', 'Unsaved changes')

            if reply:
                DB_CHANGES.commitChanges()

        event.accept()

if __name__ == '__main__':
    style_file = '/home/cnc/Public/craftisan/src/craftisan/styles/techno.qss'

    app = QApplication(sys.argv)
    app.setStyle('Fusion')


    with open(style_file, 'r') as f:
        app.setStyleSheet(f.read())
    
    splash_pix = QPixmap(':/images/dbms/tecno_splash.png')

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setWindowIcon(QIcon(':/images/icons/icon_db.png'))
    splash.setEnabled(False)
    splash.show()

    for i in range(15):
        t = time.time()
        while time.time() < t + 0.1:
           app.processEvents()

    tecno = TecnoManagerWindow()
    tecno.setGeometry(0, 0, 1915, 1011)
    tecno.setWindowTitle('Craftisan Tecno')
    tecno.showMaximized()

    splash.finish(tecno)

    sys.exit(app.exec_())
from qtpy.QtWidgets import QAction
from PyQt5.QtGui import QIcon

import craftisan.craftisan_rc

class DBActionManager:
    def __init__(self):
        self.actions = {}

    def createAction(self, name, text, icon=None, shortcut=None, callback=None):
        action = QAction(text, None)
        if icon is not None:
            action.setIcon(QIcon(icon))
        if shortcut:
            action.setShortcut(shortcut)
        if callback:
            action.triggered.connect(callback)
        self.actions[name] = action
        return action
    
    def getAction(self, name):
        return self.actions.get(name)
    
    def initialise(self):
        self.createAction('save', 'Save',':/images/dbms/save_button.png', "Ctrl+S")
        self.createAction('duplicate', 'Duplicate', ':/images/dbms/copy.png', "Ctrl+D")
        self.createAction('add_tool', 'Add tool', ':/images/dbms/add_button.png', "Ctrl+N")
        self.createAction('modify_tool', 'Modify tool', ':/images/dbms/modify_button.png', "Ctrl+M")
        self.createAction('delete_tool', 'Delete tool', ':/images/dbms/delete_button.png', "Del")
        self.createAction('apply_changes', 'Apply Changes', ':/images/dbms/apply.png', "Ctrl+Return")
        self.createAction('discard_changes', 'Discard Changes', ':/images/dbms/discard.png', "Ctrl+0")

class DBActionManager2:
    def __init__(self):
        self.save_db_action = QAction(QIcon(':/images/dbms/save_button.png'), "Save")
        self.save_db_action = QAction(QIcon(':/images/dbms/save_button.png'), "Reload tree")
        self.save_db_action = QAction(QIcon(':/images/dbms/save_button.png'), "Reload LCNC Table")
        self.duplicate_tool_action = QAction(QIcon(':/images/dbms/copy.png'), "Duplicate")

        self.add_tool_action = QAction(QIcon(':/images/dbms/add_button.png'), "Add tool")
        self.edit_tool_action = QAction(QIcon(':/images/dbms/modify_button.png'), "Modify tool")
        self.delete_tool_action = QAction(QIcon(':/images/dbms/delete_button.png'), "Delete tool")

        self.apply_changes_action = QAction(QIcon(':/images/dbms/apply.png'), "Apply Changes")
        self.discard_changes_action = QAction(QIcon(':/images/dbms/discard.png'), "Discard Changes")

        self.exit_action = QAction("Exit")
       
        self.save_db_action.setShortcut("Ctrl+S")
        self.add_tool_action.setShortcut("Ctrl+N")
        self.edit_tool_action.setShortcut("Ctrl+M")
        self.delete_tool_action.setShortcut("Del")
        self.duplicate_tool_action.setShortcut("Ctrl+D")
        self.apply_changes_action.setShortcut("Ctrl+Return")
        self.discard_changes_action.setShortcut("Ctrl+0")
        self.exit_action.setShortcut("Ctrl+Q")


from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QApplication
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThreadPool, QModelIndex, Qt, QTimer
from qtpyvcp.utilities.logger import getLogger
from craftisan.tool_db.model import Tool
from widgets.tool_changer.tool_tree import ToolTreeView
# from craftisan.ui.dialogs.tool_db.tool_tree import ToolTreeView
from craftisan.utilities.worker import Worker
from craftisan.tool_db.queries import getToolById, getUnassignedTools
from qtpyvcp.plugins import getPlugin


LOG = getLogger(__name__)


class SelectToolDialog(QDialog):
    toolData = pyqtSignal(int, int, object)

    def __init__(self, **kwargs):
        super(SelectToolDialog, self).__init__(**kwargs)

        self.tool: Tool = None
        self.tool_id: int = None
        self.changer_id: int = None
        self.pocket_number: int = None

        self.resize(540, 700)
        self.setWindowTitle("Select tool")

        self._layout = QVBoxLayout(self)
        self._action_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search ...")
        self.search_btn = QPushButton("Search")
        self.tool_tree = ToolTreeView()
        self.accept_btn = QPushButton("Select")
        self.cancel_btn = QPushButton("Close")

        self.accept_btn.setEnabled(False)

        self._action_layout.addWidget(self.cancel_btn)
        self._action_layout.addWidget(self.accept_btn)

        self._layout.addWidget(self.search_box)
        self._layout.addWidget(self.search_btn)
        self._layout.addWidget(self.tool_tree)
        self._layout.addLayout(self._action_layout)
        self.setLayout(self._layout)

        self.treeSelectionModel = self.tool_tree.selectionModel()

        self.accept_btn.clicked.connect(self.onAccept)
        self.cancel_btn.clicked.connect(self.close)
        self.search_btn.clicked.connect(self.fetchData)
        self.treeSelectionModel.currentChanged.connect(self.onCurrentChanged)
        self.tool_tree.doubleClicked.connect(self.onDoubleClick)

        self.debounce = QTimer(self)
        self.debounce.setInterval(250)
        self.debounce.setSingleShot(True)
        self.debounce.timeout.connect(self.fetchData)
        self.search_box.textEdited.connect(self.debounce.start)
        # self.search_box.returnPressed.connect(self.search_btn.click)

        self.tt = getPlugin('tooltable')

    @pyqtSlot(int, int)
    def showDialog(self, changer_id: int, pocket_number: int):
        if changer_id is None or pocket_number is None:
            return

        self.changer_id = changer_id
        self.pocket_number = pocket_number
        self.fetchData()
        self.show()

    @pyqtSlot()
    def fetchData(self):
        assigned_ids = self.tt.getAllAssignedToolIds()
        worker = Worker(getUnassignedTools,
                        self.search_box.text(), assigned_ids)
        pool = QThreadPool.globalInstance()
        worker.signals.result.connect(self.tool_tree.loadTreeData)
        pool.start(worker)

    @pyqtSlot(int)
    def fetchTool(self, toolId: int):
        worker = Worker(getToolById, toolId)
        pool = QThreadPool.globalInstance()
        worker.signals.result.connect(self.acceptTool)
        pool.start(worker)

    @pyqtSlot(object)
    def acceptTool(self, tool: Tool):
        if tool is None or self.pocket_number is None or self.changer_id is None:
            return

        self.toolData.emit(
            self.changer_id, self.pocket_number, tool.toToolTableRow())
        self.accept()
        self.search_box.setText('')

    def onAccept(self):
        self._selectTool()

    def onDoubleClick(self, index: QModelIndex):
        self._selectTool()

    def _selectTool(self):
        data = self.treeSelectionModel.currentIndex().data(Qt.UserRole)

        if not isinstance(data, dict):
            return

        if "nodeType" in data and data["nodeType"] == 'tool':
            self.fetchTool(data["id"])

    def onCurrentChanged(self, current: QModelIndex, prev):
        currentData = current.data(Qt.UserRole)

        if not isinstance(currentData, dict):
            return

        if "nodeType" in currentData and currentData["nodeType"] == 'tool':
            self.accept_btn.setEnabled(True)
        else:
            self.accept_btn.setEnabled(False)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = SelectToolDialog()
    dialog.show()
    sys.exit(app.exec())


"""
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__',
 '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
 '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_cycle_time', '_initialized', '_log', '_max_mdi_history_length', '_mdi_history_file',
 '_periodic', '_postGuiInitialized', 'acceleration', 'active_queue', 'actual_position', 'adaptive_feed_enabled', 'ain', 'allHomed', 'all_axes_homed', 'angular_jog_velocity', 'angular_units', 'aout', 'axis_mask', 'blockSignals', 'block_delete', 'call_level', 'channels', 'childEvent', 'children', 'command', 'connectNotify', 'current_line', 'current_vel', 'customEvent', 'cycle_time', 'debug', 'delay_left', 'deleteLater', 'destroyed', 'din', 'disconnect', 'disconnectNotify', 'distance_to_go', 'dout', 'dtg', 'dumpObjectInfo', 'dumpObjectTree', 'dynamicPropertyNames', 'echo_serial_number', 'enabled', 'estop', 'event', 'eventFilter', 'exec_state',
 'feed_hold_enabled', 'feed_override_enabled', 'feedrate', 'file', 'file_watcher', 'findChild', 'findChildren', 'flood', 'forceUpdateStaticChannelMembers', 'g5x_index', 'g5x_offset', 'g92_offset', 'gcodes', 'getChannel', 'homed', 'inherits', 'ini_filename', 'initialise', 'inpos', 'input_timeout', 'installEventFilter', 'interp_state', 'interpreter_errcode', 'isSignalConnected', 'isWidgetType', 'isWindowType', 'jog_increment', 'jog_mode', 'joint', 'joint_actual_position', 'joint_position', 'joints', 'killTimer', 'kinematics_type', 'limit', 'linear_jog_velocity', 'linear_units', 'loadMdiHistory', 'log', 'lube', 'lube_level', 'max_acceleration',
 'max_recent_files', 'max_velocity', 'mcodes', 'mdi_history', 'mdi_remove_all', 'mdi_remove_entry', 'mdi_swap_entries', 'metaObject', 'misc_error', 'mist',
 'motion_id', 'motion_line', 'motion_mode', 'motion_type', 'moveToThread', 'no_force_homing', 'num_extrajoints', 'objectName', 'objectNameChanged', 'old',
 'on', 'optional_stop', 'parent', 'paused', 'pocket_prepped', 'position', 'postGuiInitialise', 'probe_tripped', 'probe_val', 'probed_position', 'probing',
 'program_units', 'property', 'pyqtConfigure', 'queue', 'queue_full', 'queued_mdi_commands', 'rapidrate', 'read_line', 'receivers', 'recent_files', 'removeEventFilter', 'rotation_xy', 'saveMdiHistory',
 'sender', 'senderSignalIndex', 'setLogLevel', 'setObjectName', 'setParent', 'setProperty', 'settings', 'signalsBlocked', 'spindle', 'spindles', 'startTimer', 'stat', 'state', 'staticMetaObject', 'step_jog_increment', 'task_mode', 'task_paused', 'task_state', 'terminate', 'thread', 'timer', 'timerEvent',
 'tool_from_pocket', 'tool_in_spindle', 'tool_offset', 'tool_table', 'toolinfo', 'tr', 'updateFile', 'velocity']
"""
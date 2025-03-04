import os
import linuxcnc
from qtpy.QtCore import QTimer, QThreadPool, Signal

from craftisan.tool_db.base import Session
from craftisan.tool_db.model import Tool, Pocket, ToolChanger

from qtpyvcp.utilities.info import Info
from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.actions.machine_actions import issue_mdi
from qtpyvcp.plugins import DataPlugin, DataChannel, getPlugin
from craftisan.utilities.worker import Worker

CMD = linuxcnc.command()
LOG = getLogger(__name__)
STATUS = getPlugin('status')
STAT = STATUS.stat
INFO = Info()

IN_DESIGNER = os.getenv('DESIGNER', False)

NO_TOOL = {
    'T': 0,
    'C': 0.0,
    'D': 0.0,
    'P': 0,
    'X': 0.0,
    'Y': 0.0,
    'Z': 0.0,
    'R': 'No Tool Loaded',
}

COLUMN_LABELS = {
    'A': 'A Offset',
    'B': 'B Offset',
    'C': 'C Offset',
    'D': 'Diameter',
    'I': 'Fnt Ang',
    'J': 'Bak Ang',
    'P': 'Pocket',
    'Q': 'Orient',
    'R': 'Remark',
    'T': 'Tool',
    'U': 'U Offset',
    'V': 'V Offset',
    'W': 'W Offset',
    'X': 'X Offset',
    'Y': 'Y Offset',
    'Z': 'Z Offset',
}

class DBToolTable(DataPlugin):

    tool_table_changed = Signal(dict) # tc_id, pocket_numbers, table_data
    toolchanger_changed = Signal(int, tuple, list) # tc_id, pocket_numbers, table_data
    unsavedChnages = Signal(int, bool)
    unsavedChnagesAll = Signal(bool)

    COLUMN_LABELS = COLUMN_LABELS

    def __init__(self, columns='TPXYZCDR', remember_tool_in_spindle=True):
        super(DBToolTable, self).__init__()
        
        self.tool_table: dict[dict] = {0: NO_TOOL}
        self.tool_changers: dict[dict] = dict()
        self._current_tool = dict()
        self.remember_tool_in_spindle = remember_tool_in_spindle
        self.columns = self.validateColumns(columns) or [c for c in 'TPXYZCDR']
        self.data_manager = getPlugin('persistent_data_manager')

        # update signals
        STATUS.tool_in_spindle.notify(self.setCurrentTool)
        STATUS.all_axes_homed.notify(self.reload_tool)
        # STATUS.tool_table.notify(lambda *args: self.loadToolTable())

    def reload_tool(self):
        if self.remember_tool_in_spindle and STATUS.all_axes_homed.value and STATUS.enabled.value:
            tnum = self.data_manager.getData('tool-in-spindle', 0)
            LOG.debug(f"reload_tool(): {STAT.tool_in_spindle=}, new_tool={tnum}")
            if STAT.tool_in_spindle == 0 and tnum != STAT.tool_in_spindle:
                LOG.info(f"Reloading tool in spindle: {tnum}")
                cmd = "M61 Q{0} G43".format(tnum)
                # give LinuxCNC time to switch modes
                QTimer.singleShot(200, lambda: issue_mdi(cmd))

    def initialise(self):
        self.loadToolTable()
        self.loadToolChangers()
        # LOG.info("Initialised %s plugin"%'DBToolTable')

    def terminate(self):
        self.data_manager.setData('tool-in-spindle', STAT.tool_in_spindle)

    @DataChannel
    def current_tool(self, chan, item=None):
        """Current Tool Info

        Available items:

        * T -- tool number
        * P -- pocket number
        * X -- x offset
        * Y -- y offset
        * Z -- z offset
        * C -- c offset
        * R -- remark

        Rules channel syntax::

            tooltable:current_tool
            tooltable:current_tool?X
            tooltable:current_tool?x_offset

        :param item: the name of the tool data item to get
        :return: dict, int, float, str
        """
        if item is None:
            return self._current_tool
        return self._current_tool.get(item[0].upper())

    @staticmethod
    def validateColumns(columns):
        """Validate display column specification.

        The user can specify columns in multiple ways, method is used to make
        sure that that data is validated and converted to a consistent format.

        Args:
            columns (str | list) : A string or list of the column IDs
                that should be shown in the tooltable.

        Returns:
            None if not valid, else a list of uppercase column IDs.
        """
        if not isinstance(columns, (str, list, tuple)):
            return

        return [col for col in [col.strip().upper() for col in columns]
                if col in 'TPXYZABCUVWDIJQR' and not col == '']

    def setCurrentTool(self, tool_num):
        with Session() as session:
            tool = session.get(Tool, tool_num)

            if tool:
                self._current_tool = tool.toTableDict()
            else:
                self._current_tool = NO_TOOL.copy()

            self.current_tool.setValue(self._current_tool)

    def loadToolTable(self):
        if IN_DESIGNER:
            return
        
        worker = Worker(self._loadToolTable)
        pool = QThreadPool.globalInstance()
        pool.start(worker)
        
    def _loadToolTable(self):
        with Session() as session:
            pockets = session.query(Pocket).where(Pocket.toolId.is_not(None)).all()

            table = {0: NO_TOOL}
            table.update({
                p.tool.id: p.tool.toTableDict() 
                for p in pockets if p.tool is not None
            })
            self.tool_table = table
            self._current_tool = table[STATUS.tool_in_spindle.getValue()]
            self.current_tool.setValue(self._current_tool)

            self.tool_table_changed.emit(self.tool_table.copy())

    def loadToolChangers_old(self):
        # if IN_DESIGNER:
        #     self.current_tool.setValue(NO_TOOL.copy())
        #     return
        
        with Session() as session:
            tool_changer_ids = session.query(ToolChanger.id).all()

            for tc_id in tool_changer_ids:
                self.getToolChangerTable(tc_id[0])
        
        # LOG.info("Called %s"%'DBToolTable.loadToolChangers')

    def loadToolChangers(self):
        worker = Worker(self._loadToolChangers)
        pool = QThreadPool.globalInstance()
        pool.start(worker)

    def _loadToolChangers(self):
        if IN_DESIGNER:
            return
        
        with Session() as session:
            tool_changers = session.query(ToolChanger).all()

            self.tool_changers.update({
                tc.id: {
                    p.pocketNumber: p.toolId for p in tc.pockets
                } for tc in tool_changers
            })

            # LOG.info(f"_loadToolChangers()\n{self.tool_changers=}")
    
    def saveToolChangers(self):
        for tc_id, table in self.tool_changers.items():
            self.saveToolChangerTable(tc_id, table, reload_table=False)

        CMD.load_tool_table()

    def updateToolChanger(self, tc_id: int, tool_table: dict) -> None:
        if tc_id in self.tool_changers and self.tool_changers[tc_id]:
            self.tool_changers[tc_id].update(tool_table)
        else:
            self.tool_changers[tc_id] = tool_table.copy()

        self.unsavedChnages.emit(tc_id, True)
        self.unsavedChnagesAll.emit(True)

        # LOG.info(f"updateToolChanger()\n{self.tool_changers=}")

    def getAllOccupiedPockets(self):
        if not self.tool_changers:
            return {}
        
        return { pn: tn for d in self.tool_changers.values() for pn, tn in d.items() if tn is not None}
    
    def getAllAssignedToolIds(self):
        if not self.tool_changers:
            return tuple()
        
        return tuple(tn for d in self.tool_changers.values() for tn in d.values() if tn is not None)

    def getToolTable(self):
        # CMD.load_tool_table()
        return self.tool_table.copy()
    
    def getToolChangerTable(self, tc_id):
        with Session() as session:
            pocket_list = \
                session.query(Pocket) \
                    .where(Pocket.toolChangerId==tc_id) \
                    .order_by(Pocket.pocketNumber) \
                    .all()

            pocket_numbers = tuple(p.pocketNumber for p in pocket_list)
            tool_data = list(p.toTableRow() for p in pocket_list)

            self.toolchanger_changed.emit(tc_id, pocket_numbers, tool_data)
            self.unsavedChnages.emit(tc_id, False)
            self.unsavedChnagesAll.emit(False)


    def saveToolTable(self, *args, **kwargs):
        pass
    
    def saveToolChangerTable(self, tc_id: int, tool_table: dict, reload_table=True) -> None:
        """Write toolchanger pocket data to DB.

        Args:
            `tc_id` (int) : the ID of the toolchanger that the data is updated.
            `tool_table` (dict) : Dictionary containing pairs of `(pocketNumber, toolId)` 
                for each pocket in the selected tool changer.
        """

        with Session() as session:

            tools = []
            for toolno in tool_table.values():
                if toolno:
                    tools.append(session.get(Tool, toolno))
                else:
                    tools.append(None)
            
            pockets = session.query(Pocket) \
                .where(Pocket.pocketNumber.in_(tool_table.keys()), Pocket.toolChangerId==tc_id).all()
            
            for i in range(len(pockets)):
                pockets[i].tool = tools[i]

            session.add_all(pockets)
            session.commit()

        self.unsavedChnages.emit(tc_id, False)
        self.unsavedChnagesAll.emit(False)
        
        if reload_table:
            CMD.load_tool_table()
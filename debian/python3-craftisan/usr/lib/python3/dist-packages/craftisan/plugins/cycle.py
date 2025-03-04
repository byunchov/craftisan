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


class CycleButtons(DataPlugin):

    def __init__(self):
        super().__init__()
        
        # update signals
        self._bindSignals()

    def initialise(self):
        self._runOk()
        self._pauseOk()
        self._abortOk()

    def terminate(self):
        pass

    def _bindSignals(self):
        STATUS.estop.onValueChanged(self._runOk)
        STATUS.enabled.onValueChanged(self._runOk)
        STATUS.all_axes_homed.onValueChanged(self._runOk)
        STATUS.interp_state.onValueChanged(self._runOk)
        STATUS.file.onValueChanged(self._runOk)
        STATUS.state.onValueChanged(self._pauseOk)
        STATUS.paused.onValueChanged(self._pauseOk)
        STATUS.state.onValueChanged(self._abortOk)

    def _runOk(self, *args):
        if STAT.estop:
            ok = False
        elif not STAT.enabled:
            ok = False
        elif not STATUS.allHomed():
            ok = False
        elif not STAT.paused and not STAT.interp_state == linuxcnc.INTERP_IDLE:
            ok = False
        elif STAT.file == "":
            ok = False
        else:
            ok = True

        self.start_cycle.setValue(ok)

    def _pauseOk(self, *args):
        if STAT.state == linuxcnc.RCS_EXEC and not STAT.paused:
            ok = True
        elif STAT.paused:
            ok = False
        else:
            ok = False
        
        self.pause_cycle.setValue(ok)

    def _abortOk(self, *args):
        ok = False
        if STAT.state == linuxcnc.RCS_EXEC or STAT.state == linuxcnc.RCS_ERROR:
            ok = True

        self.abort_cycle.setValue(ok)

    @DataChannel
    def start_cycle(self, chan):
        """'Start cycle' button enable rule

        Rules channel syntax::

            cycle:start_cycle

        :return: bool
        """
        return chan.value

    @DataChannel
    def abort_cycle(self, chan):
        """'Stop cycle' button enable rule

        Rules channel syntax::

            cycle:stop_cycle

        :return: bool
        """
        return chan.value
    
    @DataChannel
    def pause_cycle(self, chan):
        """'Stop cycle' button enable rule

        Rules channel syntax::

            cycle:pause_cycle

        :return: bool
        """
        return chan.value
    
    @DataChannel
    def reset_cycle(self, chan):
        """'Stop cycle' button enable rule

        Rules channel syntax::

            cycle:reset_cycle

        :return: bool
        """
        return chan.value
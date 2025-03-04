import linuxcnc
import subprocess

# Set up logging
from qtpyvcp.utilities import logger
LOG = logger.getLogger(__name__)

from qtpyvcp.plugins import getPlugin

STATUS = getPlugin('status')
STAT = STATUS.stat

CMD = linuxcnc.command()


class hood:
    """Dust hood Actions Group"""
    @staticmethod
    def on():
        """Turns Flood coolant ON

        ActionButton syntax::

            extraction.hood.on
        """
        # LOG.debug("Turning dust hood green<ON>")
        CMD.mist(linuxcnc.MIST_ON)

    @staticmethod
    def off():
        """Turns Flood coolant OFF

        ActionButton syntax::

            extraction.hood.off
        """
        # LOG.debug("Turning dust hood red<OFF>")
        CMD.mist(linuxcnc.MIST_OFF)

    @staticmethod
    def toggle():
        """Toggles dust hood ON/OFF

        ActionButton syntax::

            extraction.hood.toggle
        """
        if STAT.mist == linuxcnc.MIST_ON:
            hood.off()
        else:
            hood.on()

    @staticmethod
    def position(pos=0):
        """Changes dust hood position

        ActionButton syntax::

            extraction.hood.position:num
        """

        # LOG.debug("Dust hood set position: green<%s>", str(pos))
        subprocess.run(["halcmd", "setp", "dust_hood.target_position", str(pos)])

class filter:
    """Mist Actions Group"""
    @staticmethod
    def on():
        """Turns aspiration ON

        ActionButton syntax::

            extraction.aspiration.on
        """
        # LOG.debug("Turning aspiration green<ON>")
        CMD.flood(linuxcnc.FLOOD_ON)

    @staticmethod
    def off():
        """Turns aspiration OFF

        ActionButton syntax::

            extraction.aspiration.off
        """
        # LOG.debug("Turning aspiration red<OFF>")
        CMD.flood(linuxcnc.FLOOD_OFF)

    @staticmethod
    def toggle():
        """Toggles aspiration ON/OFF

        ActionButton syntax::

            extraction.aspiration.toggle
        """
        if STAT.flood == linuxcnc.FLOOD_ON:
            filter.off()
        else:
            filter.on()

def _extraction_ok(widget=None):
    """Checks if it is OK to turn coolant ON.

    Args:
        widget (QWidget, optional) : Widget to enable/disable according to result.

    Atributes:
        msg (string) : The reason the action is not permitted, or empty if permitted.

    Retuns:
        bool : True if OK, else False.
    """
    if STAT.task_state == linuxcnc.STATE_ON:
        ok = True
        msg = ""
    else:
        ok = False
        msg = "Can't turn on coolant when machine is not ON"

    _extraction_ok.msg = msg

    if widget is not None:
        widget.setEnabled(ok)
        widget.setStatusTip(msg)
        widget.setToolTip(msg)

    return ok

def _hood_bindOk(widget):
    _extraction_ok(widget)
    widget.setChecked(STAT.mist == linuxcnc.MIST_ON)
    STATUS.task_state.onValueChanged(lambda: _extraction_ok(widget))
    STATUS.mist.onValueChanged(lambda s: widget.setChecked(s == linuxcnc.MIST_ON))

def _filter_bindOk(widget):
    _extraction_ok(widget)
    widget.setChecked(STAT.flood == linuxcnc.FLOOD_ON)
    STATUS.task_state.onValueChanged(lambda: _extraction_ok(widget))
    STATUS.flood.onValueChanged(lambda s: widget.setChecked(s == linuxcnc.FLOOD_ON))

hood.on.ok = hood.off.ok = hood.toggle.ok = _extraction_ok
hood.on.bindOk = hood.off.bindOk = hood.toggle.bindOk = _hood_bindOk

# hood.position.ok = _extraction_ok
# hood.position.bindOk = lambda *args, **kwargs: True

filter.on.ok = filter.off.ok = filter.toggle.ok = _extraction_ok
filter.on.bindOk = filter.off.bindOk = filter.toggle.bindOk = _filter_bindOk
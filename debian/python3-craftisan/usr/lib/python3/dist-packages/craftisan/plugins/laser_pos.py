from qtpy.QtCore import Signal
from qtpyvcp.plugins import DataPlugin, DataChannel
from qtpyvcp.actions.machine_actions import issue_mdi
from qtpyvcp.utilities.logger import getLogger
import os
import linuxcnc

LOG = getLogger(__name__)
STAT = linuxcnc.stat()
CMD = linuxcnc.command()

"""Register a plugin from a class.
.. code-block:: yaml

    data_plugins:
        laserpos:
        provider: craftisan.utils.laser_pos:LaserPosTable
        kwargs:
            init_pos: M5;G53 G0 Z-5;G53 G0 X10
            laser_pin: 9
            laser_ofs: 159.85
            pods_per_console: 4
            console_count: 6
            console_limits:
            - [66, 855]
            - [200, 1150]
            - [340, 1600]
            - [1620, 2885]
            - [1995, 3025]
            - [2325, 3165]
"""

class LaserPosTable(DataPlugin):

    errorNotifier = Signal(str)
    currConsoleChanged = Signal(int)
    currPodChanged = Signal(int)
    enableInputs = Signal(bool)
    currPosChanged = Signal(dict)

    def __init__(self, pods_per_console=4, console_count=6, console_limits=None, laser_pin=9, laser_ofs=127.69, init_pos=None):
        super(LaserPosTable, self).__init__()

        self.column_labels = ('X Pos.', *[f'Pod {i}' for i in range(1, pods_per_console+1)])
        self.row_labels = tuple(f' Rail {i} ' for i in range(1, console_count+1))

        self._col_count = len(self.column_labels)
        self._console_count = console_count
        self._pod_cnt = pods_per_console
        self.console_limits = self._validateConsoleLimits(console_limits)
        
        self._initTableData()
        self._initPositionState()

        self.position_file = None
        self.laser_pin = laser_pin
        self.laser_ofs = laser_ofs
        self.init_pos = init_pos or "M5;G53 G0 Z-5;G53 G0 X10"
        self.non_empty_consoles = []
        self._laser_homed = False
        self._initialised = False

        self._notifyPositionChange()

    def initialise(self):
        self.table_loaded.setValue(False)
        self.positioning.setValue(False)
        self._initialised = True

    def terminate(self):
        # self.saveToFile()
        pass

    def _initTableData(self):
        self.positions_table = {k: [None] * self._col_count for k in range(self._console_count)}
        self.dimentions = {k: 0.0 for k in 'lhs'}
        self.offsets = {k: 0.0 for k in 'xyz'}
        self.table_loaded.setValue(False)

    def _initPositionState(self):
        self.laser_active = False
        self.current_pod = -1
        self.current_console = -1
        self.current_pod_pos = 0
        self.current_console_pos = 0

    def setTaskMode(self, mode):
        STAT.poll()
        # if STAT.estop:
        #     ok = False
        #     msg = "Can't issue MDI commands! Machine is in ESTOP"
        # elif not STAT.enabled:
        #     ok = False
        #     msg = "Can't issue MDI commands! Machine is not ENABLED"
        # elif (STAT.homed.count(1) == STAT.joints):
        #     ok = False
        #     msg = "Can't issue MDI commands! Machine is not HOMED"
        # elif (STAT.interp_state != linuxcnc.INTERP_IDLE or STAT.state == linuxcnc.RCS_EXEC):
        #     ok = False
        #     msg = "Can't issue MDI commands! Machine is not IDLE"
        # else:
        #     ok = True,
        #     msg = ''

        if STAT.state == linuxcnc.RCS_EXEC:
            running = True
        else:
            running = STAT.task_mode == linuxcnc.MODE_AUTO \
                and STAT.interp_state != linuxcnc.INTERP_IDLE

        if running:
            return False
        else:
            CMD.mode(mode)
            return True
    
    def issueMDI(self, command):
        if self.setTaskMode(linuxcnc.MODE_MDI):
            cmds = []
            if type(command) in (list, tuple):
                cmds.extend(command)                
            elif type(command) == str:
                cmds.append(command)

            for cmd in cmds:
                CMD.mdi(cmd.strip())
                # CMD.wait_complete(30)
        else:
            msg = "Failed issuing MDI command: {}".format(command)
            CMD.error_msg(msg)

    def _validateConsoleLimits(self, console_limits=None):
        if console_limits is None or not console_limits:        
            return [
                (66, 855),
                (200, 1150),
                (340, 1600),
                (1620, 2885),
                (1995, 3025),
                (2325, 3165)
            ]
        
        return console_limits

    def _formatOffsets(self):
        pice_data = {**self.dimentions, **self.offsets}
        merged = {p: pice_data[k] for p, k in zip('xyzijk', 'lhsxyz')}
        merged['j'] += self.laser_ofs
        gcode = ['G45']
        gcode.extend([f'{k.upper()}{merged[k]:.3f}' for k in 'xyzijk'])
        
        return ' '.join(gcode)

    def getColumns(self):
        if type(self.positions_table) == dict:
            return list(self.positions_table.values())
        
        return list([None] * self._col_count for _ in range(self._col_count))
    
    def clearTable(self):
        # self.positions_table = {k: [None] * self._col_count for k in range(self._console_count)}
        self._initTableData()

    def clearTableRow(self, row):
        self.positions_table[row] = [None] * self._col_count

    def loadFromFile(self, file_path):
        if not os.path.isfile(file_path):
            self.errorNotifier.emit(f"Invalid file!\n'{file_path}'")
            return
        
        console_data = dict()

        with open(file_path, 'r') as file:
            for line in file:
                if len(line) < 6:
                    continue

                try:
                    positions = line.strip()[5:-1].split(',')
                    points = tuple(map(float, positions))
                    line_upper = line.upper()

                    if 'POS' in line_upper:
                        x_pos, y_pos = points
                        if x_pos not in console_data:
                            console_data[x_pos] = set()

                        if y_pos:
                            console_data[x_pos].add(y_pos)

                    elif 'DIM' in line_upper:
                        for key, value in zip('lhs', points):
                            self.dimentions[key] = value
                    elif 'OFS' in line_upper:
                        for key, value in zip('xyz', points):
                            self.offsets[key] = value
                    else:
                        continue
                except (ValueError, KeyError):
                    continue
        
        if not console_data:
           self.errorNotifier.emit(f"Empty file!\n'{file_path}'")
           return

        data = dict()
        for key in console_data.keys():
            for index, limits in enumerate(self.console_limits):
                if index in data:
                    continue

                if limits[0] <= key <= limits[1] and all(console_data[key]):
                    # reverse = index % 2
                    # items = sorted(console_data[key], reverse=reverse)[:self._pod_cnt]

                    items = list(console_data[key])
                    items = items[:self._pod_cnt]
                    data[index] = [key, *items]
                    arr_size = len(data[index])
                    if arr_size < self._col_count:
                        delta = self._col_count - arr_size
                        data[index] += [None] * delta

                    break

        console_numbers = set(range(self._console_count))
        consoles_with_pods = set(data.keys())
        empty_consoles = console_numbers ^ consoles_with_pods # symmetric_difference

        for console in empty_consoles:
            data[console] = [None] * self._col_count

        self.positions_table = data.copy()
        self.position_file = file_path
        self.consoles_with_pods = list(consoles_with_pods)
        self.table_loaded.setValue(self.hasData())
        # self.table_loaded.setValue(True)

    def saveToFile(self):
        if not self.position_file:
            self.errorNotifier.emit(f"Invalid file!\n'{self.position_file}'")
            return
        
        file_path = self.position_file
        file_content = []
        
        if self.dimentions:
            values = ','.join([f'{self.dimentions[k]:.3f}' for k in 'lhs'])
            file_content.append(f"#DIM({values})")
        
        if self.offsets:
            values = ','.join([f'{self.offsets[k]:.3f}' for k in 'xyz'])
            file_content.append(f"#OFS({values})")

        if self.positions_table:
            for row in range(self._console_count):
                row_data = self.positions_table[row]
                if len(row_data) > 2 and all(row_data[:2]):
                    x_pos = row_data[0]
                    for y_pos in row_data[1:]:
                        if y_pos is None or y_pos == 0:
                            continue
                        file_content.append(f"#POS({x_pos:.3f},{y_pos:.3f})")
        
        with open(file_path, 'w+') as file:
            for line in file_content:
                print(line, file=file)

    def sortRow(self, row: int, *, desc=False):        
        if not self._hasRowData(row):
            return
        
        def sort_asc(x):
            return (x is None, x)
        
        def sort_desc(x):
            return (x is not None, x)
        
        x_pos = self.positions_table[row][0]
        y_pos = self.positions_table[row][1:]
        row_data = tuple(None if x == 0 else x for x in y_pos)

        items = sorted(row_data, reverse=desc, key=sort_desc if desc else sort_asc)
        self.positions_table[row] = [x_pos, *items]

    def startLaserPointer(self):
        if not self.laser_active:
            self.laser_active = True
            # issue_mdi(f"M64 P{self.laser_pin:1.0f}", False)
            self.issueMDI(f"M64 P{self.laser_pin:1.0f}")

        self.positioning.setValue(self.laser_active)
    
    def stopLaserPointer(self):
        if self.laser_active:
            self.laser_active = False
            cmds = [f"M65 P{self.laser_pin:1.0f}", 'G45.1']
            self.issueMDI(cmds)
            # cmd = ';'.join(cmds)
            # issue_mdi(cmd)

    def togglePointer(self, state):
        if self.laser_active:
            return
        
        m_code = 'M64' if state else 'M65'
        cmd = f'{m_code} P{self.laser_pin:1.0f}'
        # issue_mdi(cmd)
        self.issueMDI(cmd)
    
    def projectPodPosition(self, pos):
        # issue_mdi(f"G0 Y{pos:.3f}", False)
        pos -= self.offsets['y']
        self.issueMDI(f"G0 Y{pos:.3f}")

    def hasData(self):
        rows = self.positions_table.values()
        return any([any(row) for row in rows])

    def _hasRowData(self, row):
        if row < 0:
            return False
        
        return all(self.positions_table[row][:2])
    
    def nextPod(self):
        """Move to the next pod on the current console."""
        if not self.laser_active:
            return

        row_key = self.non_empty_consoles[self.current_console]
        row_data = self.positions_table[row_key][1:]

        for j in range(self.current_pod + 1, len(row_data)):
            if row_data[j]:
                self.current_pod = j
                self.current_pod_pos = row_data[j] + self.offsets['y']
                self.current_console_pos = self.positions_table[row_key][0] + self.offsets['x']
                self.projectPodPosition(self.current_pod_pos)
                self.currPodChanged.emit(self.current_pod)
                self._notifyPositionChange()
                return
            
        self.nextConsole()
    
    def prevPod(self):
        """Move to the previous pod on the current console."""
        if not self.laser_active:
            return

        row_key = self.non_empty_consoles[self.current_console]
        row_data = self.positions_table[row_key][1:]

        upper_bound = self.current_pod - 1
        for j in range(upper_bound, -1, -1):
            if row_data[j]:
                self.current_pod = j
                self.current_pod_pos = row_data[j]  + self.offsets['y']
                self.current_console_pos = self.positions_table[row_key][0] + self.offsets['x']
                self.projectPodPosition(self.current_pod_pos)
                self.currPodChanged.emit(self.current_pod)
                self._notifyPositionChange()
                return
            
        self.prevConsole()
    
    def nextConsole(self):
        """Move to the next console with pods."""
        if not self.laser_active:
            return
        
        if self.current_console < 0:
            self.current_console

        size = len(self.non_empty_consoles) - 1
        if self.current_console < size:
            self.current_console += 1
            self.current_pod = -1
            self.nextPod()
        else:
            self.endPositioning()
        
        self.currConsoleChanged.emit(self.current_console)
    
    def prevConsole(self):
        """Move to the previous console with pods."""
        if not self.laser_active:
            return

        if self.current_console > 0:
            self.current_console -= 1
            # self.current_pod = 0
            self.current_pod = self._pod_cnt
            self.prevPod()
            self.currConsoleChanged.emit(self.current_console)

    def beginPositoning(self, console=0):
        if self.laser_active:
            return
        
        self.non_empty_consoles = [k for k, v in self.positions_table.items() if v[0] and any(v[1:])]

        if console not in self.non_empty_consoles:
            self.current_console = self.non_empty_consoles[0]

        self.current_console = console
        self.currConsoleChanged.emit(self.current_console)
        self.enableInputs.emit(False)

        cmds = []
        if self.init_pos:
            cmds.extend(self.init_pos.strip().split(';'))

        cmds.append('G55')
        cmds.append(self._formatOffsets())
        # cmd = ';'.join(cmds)

        self.issueMDI(cmds)
        self.startLaserPointer()
        self.nextPod()

    def endPositioning(self):
        self.stopLaserPointer()
        self._initPositionState()
        self.currConsoleChanged.emit(self.current_console)
        self.enableInputs.emit(True)
        self._notifyPositionChange()
        self.positioning.setValue(self.laser_active)

    def _notifyPositionChange(self):
        self.pod_num.setValue(self.current_pod + 1)
        self.console_num.setValue(self.current_console + 1)
        self.pod_position.setValue(self.current_pod_pos)
        self.console_position.setValue(self.current_console_pos)
    
    @DataChannel
    def pod_num(self, chan):
        """
        Current pod number

        Usage:
            laserpos:pod_num
            laserpos:pod_num?str

        :return: int
        """
        if not self.non_empty_consoles:
            return 0.0
        
        return chan.value
    
    @pod_num.tostring
    def pod_num(self, chan):
        return '{:.0f}'.format(chan.value)
    
    @DataChannel
    def console_num(self, chan):        
        """
        Current console number

        Usage:
            laserpos:console_num
            laserpos:console_num?str

        :return: int
        """
        if not self.non_empty_consoles:
            return 0.0
        
        return chan.value
    
    @console_num.tostring
    def console_num(self, chan):
        return '{:.0f}'.format(chan.value)
    
    @DataChannel
    def pod_position(self, chan):
        """
        Current pod position

        Usage:
            laserpos:pod_position
            laserpos:pod_position?str

        :return: float
        """
        if not self.non_empty_consoles:
            return 0.0
        
        return chan.value
    
    @pod_position.tostring
    def pod_position(self, chan):
        return '{:.2f}'.format(chan.value)
    
    @DataChannel
    def console_position(self, chan):
        """
        Current console position

        Usage:
            laserpos:console_position
            laserpos:console_position?str

        :return: float
        """
        if not self.non_empty_consoles:
            return 0.0
        
        return chan.value
    
    @console_position.tostring
    def console_position(self, chan):
        return '{:.2f}'.format(chan.value)

    @DataChannel
    def table_loaded(self, chan):
        """
        Table has data

        Usage:
            laserpos:table_loaded

        :return: bool
        """
        if not self._initialised:
            return False
        
        return chan.value
    
    @DataChannel
    def positioning(self, chan):
        """
        Table has data

        Usage:
            laserpos:positioning

        :return: bool
        """
        if not self._initialised:
            return False

        return chan.value

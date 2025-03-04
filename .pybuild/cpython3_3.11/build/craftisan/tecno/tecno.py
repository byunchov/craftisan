#!/usr/bin/env python3

import sys, time
import subprocess
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import QLockFile, QDir, Qt
from craftisan.tecno.tecno_manager import TecnoManagerWindow, WIN_TITLE, WIN_ICON

import craftisan.craftisan_rc


XDO_CMD = "xdotool search --onlyvisible --class {0} windowactivate --sync windowfocus --sync"

class TecnoDBApplication(QApplication):
    def __init__(self, argv):
        super(TecnoDBApplication, self).__init__(argv)

        self.instance_identifier = "TecnoDBManager"
        self.lock_file = QLockFile(QDir.temp().filePath(f"{self.instance_identifier}.lock"))
        
        if not self.lock_file.tryLock(100):
            self.activateExistingInstance()
            sys.exit(0)

        self.aboutToQuit.connect(self.cleanup)

    def activateExistingInstance(self):
        try:
            cmd = XDO_CMD.format(WIN_TITLE).split()
            subprocess.run(cmd)
        except FileNotFoundError:
            print("xdotool is not installed. Please install it `sudo apt install xdotool`.")

    def cleanup(self):
        self.lock_file.unlock()


def main():
    style_file = '/home/cnc/dev/craftisan/src/craftisan/styles/tecno.qss'

    app = TecnoDBApplication(sys.argv)
    app.setStyle('Fusion')

    with open(style_file, 'r') as f:
        app.setStyleSheet(f.read())
    
    splash_pix = QPixmap(':/images/dbms/tecno_splash.png')

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setWindowIcon(QIcon(WIN_ICON))
    splash.setEnabled(False)
    splash.show()

    for _ in range(15):
        t = time.time()
        while time.time() < t + 0.1:
           app.processEvents()

    tecno = TecnoManagerWindow()
    tecno.showMaximized()

    splash.finish(tecno)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

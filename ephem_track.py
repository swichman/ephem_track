import sys
import os
import urllib
import time
import math
import ephem
from datetime import datetime
from pathlib import Path
from PyQt4 import QtGui, uic, QtCore

class MyWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('./resources/mainWindow.ui', self)
        self.timer = QtCore.QTimer(self)

        self.FamilyList.currentItemChanged.connect(self.file_check)
        self.SatelliteList.currentItemChanged.connect(self.show_tle)
        self.UpdateTleButton.clicked.connect(self.get_tle)
        self.TrackButton.clicked.connect(self.calc_rise)
        self.timer.timeout.connect(self.disp_time)
        self.timer.start(100)

        self.FamilyList.setCurrentRow(0)
        self.file_check()
        self.show()

    def file_check(self):
        tle_file = str('.resources/tle/' + self.FamilyList.currentItem().text() + "_tlefile.txt")
        tle_old = Path(tle_file)
        if tle_old.is_file():
            self.parse_tle()
        if not tle_old.is_file():
            self.get_tle()

    def get_tle(self):
        tle = urllib.URLopener()
        tle_url = str("http://www.celestrak.com/NORAD/elements/" + self.FamilyList.currentItem().text() + ".txt")
        tle_file = str('./resources/tle/' + self.FamilyList.currentItem().text() + "_tlefile.txt")
        if os.path.exists(tle_file):
            os.remove(tle_file)
        if not os.path.exists('./resources/tle'):
            os.makedirs('./resources/tle')
        tle.retrieve(tle_url, tle_file)
        self.parse_tle()

    def parse_tle(self):
        tle_file = str('./resources/tle/' + self.FamilyList.currentItem().text() + "_tlefile.txt")
        self.SatelliteList.clear()
        global tle1
        global tle2
        tle1 = []
        tle2 = []
        i = 0
        with open(tle_file) as tlefile:
            for line in tlefile:
                if ( line[:1] != '1' ) and ( line[:1] != '2' ):
                    self.SatelliteList.addItem(line.rstrip())
                if line[:1] is '1':
                    tle1.append(line)
                if line[:1] is '2':
                    tle2.append(line)
                #i = i + 1
        self.SatelliteList.setCurrentItem(self.SatelliteList.item(0))
        self.show_tle()

    def show_tle(self):
        global tle
        pre_space = '|    '
        line1 = self.SatelliteList.currentItem().text() + '\n'
        spacer = '|===========================================================|\n'
        line2 = tle1[self.SatelliteList.currentRow()]
        line3 = tle2[self.SatelliteList.currentRow()]
        tle = line2 + line3
        self.TleTextEdit.setText(spacer + pre_space + line1 + spacer + '\n' + tle.rstrip())

    def disp_time(self):
        dtg = '{:%H:%M:%S}'.format(datetime.utcnow())
        self.UtcLcd.display(dtg)
        self.LocalLcd.display(time.strftime("%H"+":"+"%M"+":"+"%S"))

    def calc_rise(self):
        # define degrees
        degrees_per_radian = 180.0 / math.pi
        home = ephem.Observer()
        home.lon = 35.0853
        home.lat = -106.6056
        home.elevation = 1600

        iss = ephem.readtle(str(self.SatelliteList.currentItem().text()), tle1[self.SatelliteList.currentRow()], tle2[self.SatelliteList.currentRow()])
        home.date = datetime.utcnow()
        self.next_contact = home.next_pass(iss)
        duration = (self.next_contact[4] - self.next_contact[0]) * 86400
        self.time_till = (self.next_contact[0] - ephem.now()) * 86400
        self.timer.timeout.connect(self.till_rise)
        self.LogTextEdit.setText("Next pass for " + self.SatelliteList.currentItem().text() + " at %s UTC" % self.next_contact[0] + " with a duration of %d" % duration + " seconds.\nRise Az: %.3f" % (self.next_contact[1] * degrees_per_radian) + "\nFade Az: %.3f" % (self.next_contact[5] * degrees_per_radian) + "\nMax El: %.3f" % (self.next_contact[3] * degrees_per_radian))

    def till_rise(self):
        self.time_till = (self.next_contact[0] - ephem.now()) * 86400
        hh = int(self.time_till/(60*60))
        tmp = self.time_till - hh*60*60
        mm = int(tmp/60)
        ss = tmp - mm*60
        self.NextLcd.display("%d" %hh + ":%.2d" % mm + ":%.2d" % ss)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())

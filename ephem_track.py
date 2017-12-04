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

    #########################################
    #   Change this information to match    #
    #   your local lat/lon and altitude     #
    #########################################
    LocalLat = '35.105290'
    LocalLon = '-106.629355'
    LocalAlt = 1620 # meters

    #########################################
    #   Nothing needs to be changed         #
    #           below this                  #
    #########################################
    
    #########################################
    #   Initialize the window               #
    #########################################
    def __init__(self):
        super(MyWindow, self).__init__()
        # load the ui file for the windows
        uic.loadUi('./resources/mainWindow.ui', self)
        # initialize timer
        self.timer = QtCore.QTimer(self)
        # connect objects to signals
        self.FamilyList.currentItemChanged.connect(self.file_check)
        self.SatelliteList.currentItemChanged.connect(self.show_tle)
        self.UpdateTleButton.clicked.connect(self.get_tle)
        self.TrackButton.clicked.connect(self.calc_rise)
        self.timer.timeout.connect(self.disp_time)
        self.timer.start(100)
        
        self.FamilyList.setCurrentRow(0)
        self.file_check()
        self.show()
        
    #########################################
    #   Allocate TLE cache if none exists   #
    #########################################
    def file_check(self):
        tle_file = str('.resources/tle/' + self.FamilyList.currentItem().text() + "_tlefile.txt")
        tle_old = Path(tle_file)
        if tle_old.is_file():
            self.parse_tle()
        if not tle_old.is_file():
            self.get_tle()

    #########################################
    #   Download TLE's from celestrak       #
    #########################################
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

    #########################################
    #   Populate Family to Satellite list   #
    #########################################
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
                #if ( line[:1] != '1' ) and ( line[:1] != '2' ):
                if '1 ' not in line and '2 ' not in line:
                    self.SatelliteList.addItem(line.rstrip())
                if line[:1] is '1':
                    tle1.append(line)
                if line[:1] is '2':
                    tle2.append(line)
                #i = i + 1
        self.SatelliteList.setCurrentItem(self.SatelliteList.item(0))
        self.show_tle()

    #########################################
    #   Display TLE for selected satellite  #
    #########################################
    def show_tle(self):
        global tle
        pre_space = '|    '
        line1 = self.SatelliteList.currentItem().text() + '\n'
        spacer = '|===========================================================|\n'
        line2 = tle1[self.SatelliteList.currentRow()]
        line3 = tle2[self.SatelliteList.currentRow()]
        tle = line2 + line3
        self.TleTextEdit.setText(spacer + pre_space + line1 + spacer + '\n' + tle.rstrip())

    #########################################
    #   Set local and UTC clocks            #
    #########################################
    def disp_time(self):
        dtg = '{:%H:%M:%S}'.format(datetime.utcnow())
        self.UtcLcd.display(dtg)
        self.LocalLcd.display(time.strftime("%H"+":"+"%M"+":"+"%S"))

    #########################################
    #   Generate pass list, and get info    #
    #   for next pass of selected satellite #
    #########################################
    def calc_rise(self):
        # define degrees
        degrees_per_radian = 180.0 / math.pi
        home = ephem.Observer()
        home.lon = self.LocalLon
        home.lat = self.LocalLat
        home.elevation = self.LocalAlt

        target = ephem.readtle(str(self.SatelliteList.currentItem().text()), tle1[self.SatelliteList.currentRow()], tle2[self.SatelliteList.currentRow()])
        home.date = datetime.utcnow()
        self.next_contact = home.next_pass(target)
        target.compute(home)

        # Generate list of future passes
        i = home.next_pass(target)[0]
        self.PassList.clear()
        self.PassList.addItem(' Rise                        |   Fade                       |  RiseAz  |  FadeAz  |  MaxEl  |  Dur')
        while i >= self.next_contact[0] - 1:
            duration = (self.next_contact[4] - self.next_contact[0]) * 86400
            home.date = self.next_contact[4] + .02
            line = " %s    %s    %6.2f    %6.2f    %5.2f     %3d" % (self.next_contact[0], self.next_contact[4], self.next_contact[1]*degrees_per_radian, (self.next_contact[5]*degrees_per_radian), self.next_contact[3]*degrees_per_radian, duration)
            self.PassList.addItem(line)
            self.next_contact = home.next_pass(target)

        # Generate next pass info and start timer
        home.date = datetime.utcnow()
        self.next_contact = home.next_pass(target)
        target.compute(home)
        duration = (self.next_contact[4] - self.next_contact[0]) * 86400
        self.time_till = (self.next_contact[0] - ephem.now()) * 86400
        self.timer.timeout.connect(self.till_rise)
        self.LogTextEdit.setText("Next pass for " + self.SatelliteList.currentItem().text() + " at %s UTC" % self.next_contact[0] + " with a duration of %d" % duration + " seconds.\nRise Az: %.3f" % (self.next_contact[1] * degrees_per_radian) + "\nFade Az: %.3f" % (self.next_contact[5] * degrees_per_radian) + "\nMax El: %.3f" % (self.next_contact[3] * degrees_per_radian))

    #########################################
    #   calculate time till next pass       #
    #########################################
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

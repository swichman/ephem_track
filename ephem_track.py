import sys
import os
import urllib
import time
import math
import ephem
import numpy as np
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

################################################################
#       Nothing needs to be changed                            #
#               below this                                     #
################################################################
    
    #########################################
    #   Initialize the window               #
    #########################################
    def __init__(self):
        super(MyWindow, self).__init__()
        # load the ui file for the windows
        uic.loadUi('./resources/EphemTrack.ui', self)
        # initialize timer
        self.timer = QtCore.QTimer(self)
        # connect objects to signals
        self.FamilyList.currentItemChanged.connect(self.file_check)
        self.SatelliteList.itemClicked.connect(self.calc_rise)
        self.UpdateTleButton.clicked.connect(self.get_tle)
        self.TrackButton.clicked.connect(self.calc_rise)
        self.PassList.currentItemChanged.connect(self.draw_pass)
        self.timer.timeout.connect(self.disp_time)
        self.timer.start(100)
        
        self.FamilyList.setCurrentRow(0)
        self.file_check()

        self.plot.showGrid(x=True, y=True, alpha=None)
        self.plot.setXRange(0,360,padding=None,update=True)
        self.plot.setYRange(-1,91,padding=None,update=True)
        self.plot.setLimits(xMin=-1, xMax=361, yMin=-2, yMax=92)
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
            try:
                self.get_tle()
            except:
                print("No TLE files are present, and no internet connection is available")

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
        self.SatelliteList.clear()
        tle_file = str('./resources/tle/' + self.FamilyList.currentItem().text() + "_tlefile.txt")
        global tle1
        global tle2
        tle1 = []
        tle2 = []
        i = 1
        # use modulo to check while line of TLE is being read
        with open(tle_file) as tlefile:
            for line in tlefile:
                if (i % 3 == 1):
                    if i is 1:
                        self.SatelliteList.insertItem(0, line.rstrip())
                    else:
                        self.SatelliteList.addItem(line.rstrip())
                if (i % 3 == 2):
                    tle1.append(line)
                if (i % 3 == 0):
                    tle2.append(line)
                i = i + 1
        self.SatelliteList.setCurrentRow(0)
        #print(self.SatelliteList.currentItem().text())
        self.calc_rise()

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

        # build ground location
        home = ephem.Observer()
        home.lon = self.LocalLon
        home.lat = self.LocalLat
        home.elevation = self.LocalAlt
        
        # build target body
        target = ephem.readtle(str(self.SatelliteList.currentItem().text()), tle1[self.SatelliteList.currentRow()], tle2[self.SatelliteList.currentRow()])
        home.date = datetime.utcnow()

        # get next pass observed by ground location
        self.next_contact = home.next_pass(target)
        target.compute(home)
        

        # Generate list of future passes
        i = home.next_pass(target)[0]
        self.PassList.clear()
        self.PassList.addItem(' Rise                            |   Fade                       |  RiseAz  |  FadeAz  |  MaxEl  |  Dur')

        # Initialize variable arrays
        self.riseTime = []
        self.fadeTime = []
        self.maxEl = []
        self.riseAz = []
        self.fadeAz = []
        self.duration = []
        passIndex = 0

        # Iterate contacts to get list of passes
        while i >= self.next_contact[0] - 1:
            # add values to array
            self.riseTime.append(self.next_contact[0])
            self.fadeTime.append(self.next_contact[4])
            self.maxEl.append(self.next_contact[3] * degrees_per_radian)
            self.riseAz.append(self.next_contact[1] * degrees_per_radian)
            self.fadeAz.append(self.next_contact[5] * degrees_per_radian)
            self.duration.append((self.fadeTime[passIndex] - self.riseTime[passIndex]) * 86400)
            

            # Output data to screen
            line = " %s    %s    %6.2f    %6.2f    %5.2f     %3d" % (self.riseTime[passIndex],
                                                                     self.fadeTime[passIndex],
                                                                     self.riseAz[passIndex],
                                                                     self.fadeAz[passIndex],
                                                                     self.maxEl[passIndex],
                                                                     self.duration[passIndex])
            self.PassList.addItem(line)

            # Look for next contact
            home.date = self.fadeTime[passIndex] + .02
            self.next_contact = home.next_pass(target)

            # Increment index
            passIndex += 1

        # Generate next pass info and start timer
        home.date = datetime.utcnow()
        self.next_contact = home.next_pass(target)
        target.compute(home)
        duration = (self.next_contact[4] - self.next_contact[0]) * 86400
        self.time_till = (self.next_contact[0] - ephem.now()) * 86400
        self.timer.timeout.connect(self.till_rise)

    #########################################
    #   draw angles to graph                #
    #########################################
    def draw_pass(self):
        # y = a(x-rise)(x-fade)
        # a = y/(x-rise)(x-fade) when y is maxEl at midpoint

        currentIndex = self.PassList.currentRow() - 1
        if self.riseAz[currentIndex] < self.fadeAz[currentIndex]:
            mid = (self.fadeAz[currentIndex] - self.riseAz[currentIndex])/2
            a = -self.maxEl[currentIndex]/np.power((self.riseAz[currentIndex] - mid),2)
        else:
            mid = (self.riseAz[currentIndex] - self.fadeAz[currentIndex])/2
            a = -self.maxEl[currentIndex]/np.power((self.fadeAz[currentIndex] - mid),2)

        lin = np.linspace(0,360,3600)
        y = []
        for x in lin:
            test = (a * np.power((x - mid),2)) + self.maxEl[currentIndex]
            if test <= 0:
                test = 0
            y.append(test)

        y = np.asarray(y)
        self.plot.clear()
        if self.riseAz[currentIndex] < self.fadeAz[currentIndex]:
            self.plot.plot(lin, y, pen=(255,0,0,200))
        else:
            self.plot.plot(lin, y, pen=(50,50,255,200))


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

import sys
from PyQt4 import QtGui, QtCore
import time
from time import strftime
from datetime import datetime
import os
import math
import urllib
import ephem


class pyphem(QtGui.QWidget):

    def __init__(self):
        super(pyphem, self).__init__()
        self.run_window()

    def run_window(self):
        w = 740; h = 340
        self.time_lcd = QtGui.QLCDNumber(self)
        self.time_lcd.setDigitCount(8)
        self.time_lcd.setSegmentStyle(2)
        self.time_utc = QtGui.QLCDNumber(self)
        self.time_utc.setDigitCount(8)
        self.time_utc.setSegmentStyle(2)
        self.time_next = QtGui.QLCDNumber(self)
        self.time_next.setDigitCount(8)
        self.time_next.setSegmentStyle(2)

        self.exit_btn = QtGui.QPushButton('Exit',self)
        self.back_btn = QtGui.QPushButton('Back',self)
        self.tle_disp = QtGui.QTextBrowser(self)
        self.rise_disp = QtGui.QTextBrowser(self)
        self.timer = QtCore.QTimer(self)

        self.exit_btn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.back_btn.clicked.connect(self.back)
        self.timer.timeout.connect(self.disp_time)
        self.timer.start(100)
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.time_lcd)
        hbox.addWidget(self.time_utc)
        hbox.addStretch(1)
        hbox.addWidget(self.time_next)
        hbox.addStretch(1)
        hbox.addWidget(self.back_btn)
        hbox.addWidget(self.exit_btn)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.tle_disp)
        vbox.addWidget(self.rise_disp)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setGeometry(500,400,550,220)
        self.setWindowTitle('Py Ephem Tracker')
        self.import_tle()
        self.resize(w, h)
        self.show()

    def back(self):
        self.close()
        os.system('python main.py')

    def disp_time(self):
        dtg = '{:%H:%M:%S}'.format(datetime.utcnow())
        self.time_utc.display(dtg)
        self.time_lcd.display(strftime("%H"+":"+"%M"+":"+"%S"))

    def import_tle(self):
        global sat_name
        global tle1
        global tle2
        global tmp_file
        # download latest info from NASA
        tmp_file = str('tle_active.txt')
        input_file = open(tmp_file, 'r')
        sat_name = input_file.readline()
        tle1 = input_file.readline()
        tle2 = input_file.readline()
        input_file.close()

        # format TLE for use
        tle1 = tle1.strip()
        tle2 = tle2.strip()
        tle = " " + tle1 + '\n ' + tle2
        
        text = str("TLE for " + sat_name + "|===========================================================|\n" + tle)
        self.tle_disp.setText(text)
        self.calc_rise()


    def calc_rise(self):
        # define degrees
        degrees_per_radian = 180.0 / math.pi
        home = ephem.Observer()
        home.lon = 35.0853
        home.lat = -106.6056
        home.elevation = 1600

        iss = ephem.readtle(sat_name, tle1, tle2)
        home.date = datetime.utcnow()
        self.next_contact = home.next_pass(iss)
        duration = (self.next_contact[4] - self.next_contact[0]) * 86400
        self.time_till = (self.next_contact[0] - ephem.now()) * 86400
        self.timer.timeout.connect(self.till_rise)
        self.rise_disp.setText("Next pass at %s UTC" % self.next_contact[0] + " with a duration of %d" % duration + " seconds.\nRise Az: %.3f" % (self.next_contact[1] * degrees_per_radian) + "\nFade Az: %.3f" % (self.next_contact[5] * degrees_per_radian) + "\nMax El: %.3f" % (self.next_contact[3] * degrees_per_radian))

    def till_rise(self):
        self.time_till = (self.next_contact[0] - ephem.now()) * 86400
        hh = int(self.time_till/(60*60))
        tmp = self.time_till - hh*60*60
        mm = int(tmp/60)
        ss = tmp - mm*60
        self.time_next.display("%d" %hh + ":%.2d" % mm + ":%.2d" % ss)

def main():
    app = QtGui.QApplication(sys.argv)
    test = pyphem()
    test.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

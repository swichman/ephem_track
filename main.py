import sys
from PyQt4 import QtGui, QtCore
import os
import urllib
from pathlib import Path

class start_prog(QtGui.QWidget):
    
    def __init__(self):
        super(start_prog, self).__init__()
        self.build_window()

        
    def build_window(self):
        w = 740; h = 240
        self.tle_file = ''
        self.select_type = QtGui.QComboBox()
        self.select_body = QtGui.QComboBox()
        self.update_tle = QtGui.QPushButton('Update TLE', self)
        self.track = QtGui.QPushButton('Track', self)
        self.tle_show_box = QtGui.QTextBrowser()

        self.select_type.addItem('NOAA')
        self.select_type.addItem('ARGOS')
        self.select_type.addItem('Iridium')
        self.select_type.addItem('cubesat')
        self.select_type.addItem('Amateur')

        self.select_type.currentIndexChanged.connect(self.file_check)
        self.select_body.activated.connect(self.show_tle)
        self.update_tle.clicked.connect(self.get_tle)
        self.track.clicked.connect(self.selected)
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.select_type)
        hbox.addWidget(self.select_body)
        hbox.addWidget(self.update_tle)
        hbox.addWidget(self.track)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.tle_show_box)
        vbox.addLayout(hbox)

        self.file_check()
        self.setLayout(vbox)
        self.setGeometry(500,400,550,220)
        self.setWindowTitle('Py Ephem Tracker')
        self.resize(w, h)
        self.show()
        self.get_tle()

    def file_check(self):
        tle_file = str('./tle/' + self.select_type.currentText() + "_tlefile.txt")
        tle_old = Path(tle_file)
        if tle_old.is_file():
            self.parse_tle()
        if not tle_old.is_file():
            self.get_tle()

    def selected(self):
        self.close()
        tmp_name = 'tle_active.txt'
        tmp = open(tmp_name,'w')
        tmp.write(tle)
        tmp.close()
        command = str('python track.py ')
        os.system(command)

    def show_tle(self):
        global tle
        pre_space = '|    '
        line1 = self.select_body.currentText()
        spacer = '|===========================================================|\n'
        line2 = tle1[self.select_body.currentIndex()]
        line3 = tle2[self.select_body.currentIndex()]
        tle = line1 + line2 + line3
        self.tle_show_box.setText(spacer + pre_space + line1 + spacer + tle)

    def get_tle(self):
        tle = urllib.URLopener()
        tle_url = str("http://www.celestrak.com/NORAD/elements/" + self.select_type.currentText() + ".txt")
        tle_file = str('./tle/' + self.select_type.currentText() + "_tlefile.txt")
        if os.path.exists(tle_file):
            os.remove(tle_file)
        if not os.path.exists('./tle'):
            os.makedirs('tle')
        tle.retrieve(tle_url, tle_file)
        self.parse_tle()

    def parse_tle(self):
        tle_file = str('./tle/' + self.select_type.currentText() + "_tlefile.txt")
        self.select_body.clear()
        global tle1
        global tle2
        tle1 = []
        tle2 = []
        i = 0
        with open(tle_file) as tlefile:
            for line in tlefile:
                if ( line[:1] != '1' ) and ( line[:1] != '2' ):
                    self.select_body.addItem(line)
                if line[:1] is '1':
                    tle1.append(line)
                if line[:1] is '2':
                    tle2.append(line)
                i = i + 1
        self.show_tle()

def main():
    app = QtGui.QApplication(sys.argv)
    running = start_prog()
    running.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

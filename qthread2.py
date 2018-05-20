#! /usr/bin/env python3
#  -*- coding:utf-8 -*-

import numbers, time
import sys, os
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import QSettings
from m3890d import M3890D

import numpy
from pyqtgraph import AxisItem
from datetime import datetime, timedelta
from time import mktime


class DateAxisItem(AxisItem):

    # Max width in pixels reserved for each label in axis
    _pxLabelWidth = 80

    def __init__(self, *args, **kwargs):
        AxisItem.__init__(self, *args, **kwargs)
        self._oldAxis = None

    def tickValues(self, minVal, maxVal, size):

        maxMajSteps = int(size/self._pxLabelWidth)

        dt1 = datetime.fromtimestamp(minVal)
        dt2 = datetime.fromtimestamp(maxVal)

        dx = maxVal - minVal
        majticks = []

        if dx > 63072001:  # 3600s*24*(365+366) = 2 years (count leap year)
            d = timedelta(days=366)
            for y in range(dt1.year + 1, dt2.year):
                dt = datetime(year=y, month=1, day=1)
                majticks.append(mktime(dt.timetuple()))

        elif dx > 5270400:  # 3600s*24*61 = 61 days
            d = timedelta(days=31)
            dt = dt1.replace(day=1, hour=0, minute=0,
                             second=0, microsecond=0) + d
            while dt < dt2:
                # make sure that we are on day 1 (even if always sum 31 days)
                dt = dt.replace(day=1)
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 172800:  # 3600s24*2 = 2 days
            d = timedelta(days=1)
            dt = dt1.replace(hour=0, minute=0, second=0, microsecond=0) + d
            while dt < dt2:
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 7200:  # 3600s*2 = 2hours
            d = timedelta(hours=1)
            dt = dt1.replace(minute=0, second=0, microsecond=0) + d
            while dt < dt2:
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 1200:  # 60s*20 = 20 minutes
            d = timedelta(minutes=10)
            dt = dt1.replace(minute=(dt1.minute // 10) * 10,
                             second=0, microsecond=0) + d
            while dt < dt2:
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 120:  # 60s*2 = 2 minutes
            d = timedelta(minutes=1)
            dt = dt1.replace(second=0, microsecond=0) + d
            while dt < dt2:
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 20:  # 20s
            d = timedelta(seconds=10)
            dt = dt1.replace(second=(dt1.second // 10) * 10, microsecond=0) + d
            while dt < dt2:
                majticks.append(mktime(dt.timetuple()))
                dt += d

        elif dx > 2:  # 2s
            d = timedelta(seconds=1)
            majticks = range(int(minVal), int(maxVal))

        else:  # <2s , use standard implementation from parent
            return AxisItem.tickValues(self, minVal, maxVal, size)

        L = len(majticks)
        if L > maxMajSteps:
            majticks = majticks[::int(numpy.ceil(float(L) / maxMajSteps))]

        return [(d.total_seconds(), majticks)]

    def tickStrings(self, values, scale, spacing):

        ret = []
        if not values:
            return []

        if spacing >= 31622400:  # 366 days
            fmt = "%Y"
        elif spacing >= 2678400:  # 31 days
            fmt = "%Y %b"
        elif spacing >= 86400:  # 1 day
            fmt = "%b/%d"
        elif spacing >= 3600:  # 1 h
            fmt = "%b/%d-%Hh"
        elif spacing >= 60:  # 1 m
            fmt = "%H:%M"
        elif spacing >= 1:  # 1s
            fmt = "%H:%M:%S"
        else: # less than 2s (show microseconds)
            fmt = '[+%fms]'

        for x in values:
            try:
                t = datetime.fromtimestamp(x)
                ret.append(t.strftime(fmt))
            except ValueError:
                ret.append('')

        return ret

    def attachToPlotItem(self, plotItem):

        self.setParentItem(plotItem)
        viewBox = plotItem.getViewBox()
        self.linkToView(viewBox)
        self._oldAxis = plotItem.axes[self.orientation]['item']
        self._oldAxis.hide()
        plotItem.axes[self.orientation]['item'] = self
        pos = plotItem.axes[self.orientation]['pos']
        plotItem.layout.addItem(self, *pos)
        self.setZValue(-1000)


class Worker(QtCore.QThread):

    data = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self._stopped = True
        self._mutex = QtCore.QMutex()

    def stop(self):
        self._mutex.lock()
        self._stopped = True
        self._mutex.unlock()

    def run(self):
        self._stopped = False
        err = 0
        with M3890D() as dmm:
            while self._stopped == False:
                #if self._stopped:
                    #break

                time.sleep(0.5)
                try:
                    # Send USB Control Message
                    dmm.control()
                    # Capture 8-byte msg data on 0x81
                    ddata = dmm.receive();
                    # Make sure we start with the right msg order
                    if ddata[6] == 250 and ddata[7] == 250:
                        # This is wrong, get the next
                        continue;
                    time.sleep(0.02)
                    dmm.control()
                    # Extend first msg with second, cut last four 0xFA bytes
                    # and form the full 12-byte datagram
                    ddata.extend(dmm.receive()[0:4]);

                    mode = dmm.decode_mode(ddata)
                    disp = dmm.display_value(ddata)

                    if len(disp) > 0:
                        data = {
                            'message': 'running [%d]' % (
                                QtCore.QThread.currentThreadId()),
                            'time': QtCore.QTime.currentTime(),
                            'mode': mode,
                            'disp': disp
                        }
                        #print ("emit data")
                        #print (disp)
                        self.data.emit(data)
                except:
                    # catch USB disconnects and reconnect smoothly
                    err = err+1
                    if err > 3:
                        print ("Reset")
                        time.sleep(0.5)
                        dmm.open()
                        err=0
                    pass

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(508, 300)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(150, 250, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.sl_value = QtWidgets.QSlider(Dialog)
        self.sl_value.setGeometry(QtCore.QRect(220, 120, 161, 31))
        self.sl_value.setOrientation(QtCore.Qt.Horizontal)
        self.sl_value.setObjectName("sl_value")
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)


class DMMAPP(QtWidgets.QMainWindow):

    _serial_connected = False
    _serial_connecting = False
    _current_serial_ports = None
    _start_scan = False

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.y = []
        self.x = []
        self.mode = None
        self.plotColor = (128, 153, 57)

        self.settings = QSettings("COMPANY_NAME", "APPLICATION_NAME")

        self._worker = Worker()
        self._worker.started.connect(self.worker_started_callback)
        self._worker.finished.connect(self.worker_finished_callback)
        self._worker.data.connect(self.worker_data_callback)

        self.ui = uic.loadUi('qt.ui', self)
        self.ui.setWindowTitle('DMM-3890D')

        geometry = self.settings.value('geometry', '')

        if len(geometry) > 0:
            print("loading last screen size")
            self.restoreGeometry(geometry)

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'logo.png'))

        axis = DateAxisItem(orientation='bottom')
        axis.attachToPlotItem(self.plotMain.getPlotItem())
        self.plotMain.plotItem.showGrid(True, True, 0.7)
        self.plotMain.plotItem.setContentsMargins(10, 5, 10, 15)

        #self.ui.startButton.setIcon(QtGui.QIcon('start.png'))
        self.ui.pushButton.clicked.connect(self.open_new_dialog)
        self.ui.plotResetBut.clicked.connect(self.clear_plot)

        self.ui.show()
        self._worker.start()

    def clear_plot(self):
        self.y = []
        self.x = []
        self.plotMain.setDownsampling(auto=False)

    def worker_started_callback(self):
        print("worker started")
        #self.ui.startButton.setIcon(QtGui.QIcon('stop.png'))
        #pass

    def worker_finished_callback(self):
        print("worker stopped")
        #self.ui.startButton.setIcon(QtGui.QIcon('start.png'))
        #pass

    def worker_data_callback(self, data):
        print (data)
        self.ui.lcdMain.display(data['disp'][0])
        if data['disp'][1] != "aaaa":
            self.ui.lcdSub1.display(data['disp'][1])
        else:
            self.ui.lcdSub1.display("")
        self.ui.lcdSub2.display(data['disp'][2])

        if self.mode is not data['mode'][0]:
            print ("mode updated")
            self.y = []
            self.x = []
            self.plotMain.setDownsampling(auto=False)
            self.mode = data['mode'][0]
            self.update_mode_display(data)

        try:
            if isinstance(float(data['disp'][0]), numbers.Real):
                self.y.append(float(data['disp'][0]))
                self.x.append(time.time())
        except:
            pass

        if len(self.y) == 10:
            self.plotMain.setDownsampling(auto=True, mode='peak')

        self.plotMain.plot(y=self.y, x=self.x, pen=self.plotColor, symol='o', clear=True)
        labelStyle = { 'color': 'rgb('+str(self.plotColor[0])+', \
                                     '+str(self.plotColor[1])+', \
                                     '+str(self.plotColor[2])+');' }
        self.plotMain.setLabel('left', data['mode'][0], data['mode'][1], **labelStyle)

        #print(data['disp'])

    def update_mode_display(self, data):

        cssGreyHi = 'border: 1px solid rgb(232, 227, 213); background: rgba(232, 227, 213, 0.8); margin: 0; color: #0f0e0a;'
        cssGreyLo = 'border: 1px solid rgba(232, 227, 213, 0.15); background: rgba(232, 227, 213, 0.2); margin: 0; color: #0f0e0a;'
        cssYelHi  = 'border: 1px solid rgb(234, 202, 39); background: rgba(234, 202, 39, 0.8); margin: 0; color: #0f0e0a;'
        cssYelLo  = 'border: 1px solid rgba(234, 202, 39, 0.15); background: rgba(234, 202, 39, 0.2); margin: 0; color: #0f0e0a;'
        cssBluHi  = 'border: 1px solid rgb(51, 121, 234); background: rgba(51, 121, 234, 0.8); margin: 0; color: #0f0e0a;'
        cssBluLo  = 'border: 1px solid rgba(51, 121, 234, 0.15); background: rgba(51, 121, 234, 0.2); margin: 0; color: #0f0e0a;'
        cssRedHi  = 'border: 1px solid rgb(216, 54, 54); background: rgba(216, 54, 54, 0.8); margin: 0; color: #0f0e0a;'
        cssRedLo  = 'border: 1px solid rgba(216, 54, 54, 0.15); background: rgba(216, 54, 54, 0.2); margin: 0; color: #0f0e0a;'


        palette = self.ui.lcdMain.palette()

        if data['mode'][0] == "Resistance":
            self.ui.modeRes.setStyleSheet(cssYelHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(234, 202, 39)')
            palette.setColor(palette.WindowText, QtGui.QColor(234, 202, 39))
            self.plotColor = (234, 202, 39)
        else:
            self.ui.modeRes.setStyleSheet(cssYelLo)

        if data['mode'][0] == "Diode":
            self.ui.modeDiode.setStyleSheet(cssYelHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(234, 202, 39)')
            palette.setColor(palette.WindowText, QtGui.QColor(234, 202, 39))
            self.plotColor = (234, 202, 39)
        else:
            self.ui.modeDiode.setStyleSheet(cssYelLo)

        if data['mode'][0] == "DC Voltage" or data['mode'][0] == "AC Voltage":
            self.ui.modeVolt.setStyleSheet(cssGreyHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(232, 227, 213)')
            palette.setColor(palette.WindowText, QtGui.QColor(232, 227, 213))
            self.plotColor = (232, 227, 213)
        else:
            self.ui.modeVolt.setStyleSheet(cssGreyLo)

        if data['mode'][0] == "Frequency":
            self.ui.modeFreq.setStyleSheet(cssGreyHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(232, 227, 213)')
            palette.setColor(palette.WindowText, QtGui.QColor(232, 227, 213))
            self.plotColor = (232, 227, 213)
        else:
            self.ui.modeFreq.setStyleSheet(cssGreyLo)

        if data['mode'][0] == "hFE":
            self.ui.modehFE.setStyleSheet(cssGreyHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(232, 227, 213)')
            palette.setColor(palette.WindowText, QtGui.QColor(232, 227, 213))
            self.plotColor = (232, 227, 213)
        else:
            self.ui.modehFE.setStyleSheet(cssGreyLo)

        if data['mode'][0] == "Signal":
            self.ui.modeSO.setStyleSheet(cssYelHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(234, 202, 39)')
            palette.setColor(palette.WindowText, QtGui.QColor(234, 202, 39))
            self.plotColor = (234, 202, 39)
        else:
            self.ui.modeSO.setStyleSheet(cssYelLo)

        if data['mode'][0] == "Logic":
            self.ui.modeLogic.setStyleSheet(cssBluHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(51, 121, 234)')
            palette.setColor(palette.WindowText, QtGui.QColor(51, 121, 234))
            self.plotColor = (51, 121, 234)
        else:
            self.ui.modeLogic.setStyleSheet(cssBluLo)

        if data['mode'][0] == "Capacitance":
            self.ui.modeCap.setStyleSheet(cssBluHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(51, 121, 234)')
            palette.setColor(palette.WindowText, QtGui.QColor(51, 121, 234))
            self.plotColor = (51, 121, 234)
        else:
            self.ui.modeCap.setStyleSheet(cssBluLo)

        if data['mode'][0] == "Temperature":
            self.ui.modeTemp.setStyleSheet(cssBluHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(51, 121, 234)')
            palette.setColor(palette.WindowText, QtGui.QColor(51, 121, 234))
            self.plotColor = (51, 121, 234)
        else:
            self.ui.modeTemp.setStyleSheet(cssBluLo)

        if data['mode'][0] == "DC Current uA":
            self.ui.modeuA.setStyleSheet(cssRedHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(216, 54, 54)')
            palette.setColor(palette.WindowText, QtGui.QColor(216, 54, 54))
            self.plotColor = (216, 54, 54)
        else:
            self.ui.modeuA.setStyleSheet(cssRedLo)

        if data['mode'][0] == "DC Current mA":
            self.ui.modemA.setStyleSheet(cssRedHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(216, 54, 54)')
            palette.setColor(palette.WindowText, QtGui.QColor(216, 54, 54))
            self.plotColor = (216, 54, 54)
        else:
            self.ui.modemA.setStyleSheet(cssRedLo)

        if data['mode'][0] == "DC Current A":
            self.ui.modeA.setStyleSheet(cssRedHi)
            self.ui.mainUnit.setStyleSheet('color: rgb(216, 54, 54)')
            palette.setColor(palette.WindowText, QtGui.QColor(216, 54, 54))
            self.plotColor = (216, 54, 54)
        else:
            self.ui.modeA.setStyleSheet(cssRedLo)

        # set the palette
        self.ui.lcdMain.setPalette(palette)

        # update main unit value
        self.ui.mainUnit.setText(data['mode'][1])

    def closeEvent(self, event):

        if self.ui.windowState() == QtCore.Qt.WindowNoState:
            geometry = self.saveGeometry()
            self.settings.setValue('geometry', geometry)
            super(DMMAPP, self).closeEvent(event)

    def open_new_dialog(self):
        self.nd = Ui_Dialog()
        self.nd.setupUi(self.nd)


def main():
    app = QtWidgets.QApplication(sys.argv)
    DMMAPP()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

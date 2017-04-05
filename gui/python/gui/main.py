import os.path
from time import sleep

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QStatusBar, QLabel, QWidget, QHBoxLayout, QFrame, QSplitter, QStyleFactory, QMainWindow, QTextEdit, QAction, QApplication
from pyqtgraph import PlotWidget, AxisItem, ViewBox

from gui.mainwindow import Ui_MainWindow
from lib.powermonitor import PowerMonitor


# powermonitor driver
# import gui from qt designer
pm = PowerMonitor()


class TimeAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        return [QTime().addMSecs(value).toString('mm:ss') for value in values]


class Main(QMainWindow, Ui_MainWindow):
    
        
    def __init__(self):
        super().__init__()
        
        self.setupUi(self)
        
        # init variables
        
        self.xBV = []
        self.yBV = []
        self.yCA = []
        self.yPO = []
        
        self.yConsumption = []
        self.yConsumptionAcc = 0
        
        self.yConsumptionMean = []
        self.yPowerAcc = 0
        self.yConspumtionCount = 0
        
        self.xCount = 0
        
        self.maxPointsToDisplayEnabled = True
        self.maxPointsToDisplay = 1000
        self.maxPointsToStoreEnabled = False
        self.maxPointsToStore = 100000
        self.chkAlwaysScrollToRightEnabled = True
        
        self.linkXAxisValue = False
        
        self.chkSaveToFileEnabled = False
        self.saveToFileName = None
        self.fileToSave = None
        
        # init ui
        
        self.initUI()
        self.initStatusbar()
        
        self.initCmbComPorts()
        
        self.timer = QTimer()        
        self.timerPlot = QTimer()
        self.timer.timeout.connect(self.updateChartData)
        self.timerPlot.timeout.connect(self.updateCharts)
        
        # connect to pm signals
        pm.measurement_started.connect(self.measurement_started_evt)
        pm.measurement_stopped.connect(self.measurement_stopped_evt)
        pm.thread_started.connect(self.thread_started_evt)
        pm.thread_stopped.connect(self.thread_stopped_evt)
        pm.events_per_second.connect(self.events_per_second_evt)
        
        print("Timer initialized")
    
    def initCmbComPorts(self):
        ports = pm.listPorts()
        self.cmbComPort.clear()
        for port in ports:
            self.cmbComPort.addItem(port)

            
    def widgetToggleVisibility(self, value, widget):
        if value:
            widget.show()
        else:
            widget.hide()
            
    def menuBV(self, value):
        self.widgetToggleVisibility(value, self.plotBV)
    
    def menuCA(self, value):
        self.widgetToggleVisibility(value, self.plotCA)    
        
    def menuPO(self, value):
        self.widgetToggleVisibility(value, self.plotPO)
        
    def menuConsumption(self, value):
        self.widgetToggleVisibility(value, self.plotConsumption)
        
    def menuConsumptionMean(self, value):
        self.widgetToggleVisibility(value, self.plotConsumptionMean)
        
    def txtMaxPointsToDisplayEdited(self):
        self.setMaxPointsToDisplay(int(self.txtMaxPointsToDisplay.text()))
    
    def txtMaxPointsToStoreEdited(self):
        self.maxPointsToStore = int(self.txtMaxPointsToStore.text())
        
    def linkXAxis(self, link):
        if link:
            self.plotCA.setXLink(self.plotBV)
            self.plotPO.setXLink(self.plotCA)
            self.plotConsumption.setXLink(self.plotPO)
            self.plotConsumptionMean.setXLink(self.plotConsumption)
        else:
            self.plotCA.setXLink(None)
            self.plotPO.setXLink(None)
            self.plotConsumption.setXLink(None)
            self.plotConsumptionMean.setXLink(None)
    
    def limitMaxPointsToStore(self, limit):
        self.txtMaxPointsToStore.setReadOnly(not limit)
        self.maxPointsToStoreEnabled = limit
    
    def limitMaxPointsToDisplay(self, limit):
        self.txtMaxPointsToDisplay.setReadOnly(not limit)
        self.maxPointsToDisplayEnabled = limit
                
        if self.maxPointsToDisplayEnabled:
            self.plotBV.setLimits(maxXRange=self.maxPointsToDisplay)
            self.plotCA.setLimits(maxXRange=self.maxPointsToDisplay)
            self.plotPO.setLimits(maxXRange=self.maxPointsToDisplay)
            self.plotConsumption.setLimits(maxXRange=self.maxPointsToDisplay)
            self.plotConsumptionMean.setLimits(maxXRange=self.maxPointsToDisplay)
        else:
            self.plotBV.setLimits(maxXRange=None)
            self.plotCA.setLimits(maxXRange=None)
            self.plotPO.setLimits(maxXRange=None)
            self.plotConsumption.setLimits(maxXRange=None)
            self.plotConsumptionMean.setLimits(maxXRange=None)
            
            self.btnResetXAxisPressed()
            
        self.scrollToRight()
        
    
    def chkAlwaysScrollToRightToggled(self, value):
        self.chkAlwaysScrollToRightEnabled = value
        self.scrollToRight()
        
    def setMaxPointsToDisplay(self, points):
        self.maxPointsToDisplay = points

        
    def btnResetXAxisPressed(self):
        self.plotBV.enableAutoRange(axis=ViewBox.XAxis, enable=True)
        self.plotCA.enableAutoRange(axis=ViewBox.XAxis, enable=True)
        self.plotPO.enableAutoRange(axis=ViewBox.XAxis, enable=True)
        self.plotConsumption.enableAutoRange(axis=ViewBox.XAxis, enable=True)
        self.plotConsumptionMean.enableAutoRange(axis=ViewBox.XAxis, enable=True)

    def btnResetYAxisPressed(self):
        self.plotBV.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        self.plotCA.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        self.plotPO.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        self.plotConsumption.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        self.plotConsumptionMean.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        
    def btnConnectPressed(self):
        if pm.isThreadRunning():
            pm.stopMeasurement()
            sleep(0.1)
            pm.stopThread()
            
        else:
            pm.startThread(self.cmbComPort.itemText(self.cmbComPort.currentIndex()))

    def measurement_started_evt(self):
        self.btnStartStop.setText("Stop")
        self.sbLblMeasurementState.setText("Measurement running")
        
        self.timer.start(50)
        self.timerPlot.start(1000)
        
        if self.chkSaveToFile.isChecked():
            name = self.txtSaveToFileName.text()
            
            self.fileToSave =open(name, "w")
            self.chkSaveToFile.setEnabled(False)
        
        
    def measurement_stopped_evt(self):
        self.btnStartStop.setText("Start")
        self.sbLblMeasurementState.setText("Measurement not running")

        self.timer.stop()
        self.timerPlot.stop()
        
        if self.chkSaveToFile.isChecked() and self.fileToSave is not None:
            self.fileToSave.close()
            
            self.chkSaveToFile.setEnabled(True)
        
    def thread_started_evt(self):
        self.sbLblConnectionState.setText("Serial connected")
        self.btnConnect.setText("Disconnect")
        self.cmbComPort.setEnabled(False)
        self.btnStartStop.setEnabled(True)
        
        
        
    def thread_stopped_evt(self):
        self.sbLblConnectionState.setText("Serial not connected")
        self.btnConnect.setText("Connect")
        self.cmbComPort.setEnabled(True)
        
        #self.btnStartStop.setText("Start")
        self.btnStartStop.setEnabled(False)
        
    
    def events_per_second_evt(self, eps):
        self.setEps(eps)
        
    def btnStartStopPressed(self):
        if not pm.isMeasurementRunning():
            start = True
            
            # first, check if save to file is enabled and if file is writable
            if self.chkSaveToFile.isChecked():
                name = self.txtSaveToFileName.text()
                
                if not os.path.exists(name):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("The specified file does not exist")
                    msg.setInformativeText("File: " + name)
                    msg.setWindowTitle("File not found")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    
                    start = False
                    
                if not os.path.isfile(name):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("The specified file is not a file")
                    msg.setInformativeText("File: " + name)
                    msg.setWindowTitle("Not a file")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    
                    start = False
                    
            if start:
                pm.startMeasurement()
                
        else:
            pm.stopMeasurement()
    
    def setEps(self, eps):
        self.sbLblEps.setText("{: .2f} e/s".format(eps))
        
    def chooseFile(self):
        filename = QFileDialog.getSaveFileName(self, 'Save file', '', "PM file (*.pmlog)")
        self.setSaveToFileName(filename[0])
        
    def setSaveToFileName(self, name):
        self.txtSaveToFileName.setText(name)
        
    def chkSaveToFileToggled(self, enabled):
        self.chkSaveToFileEnabled = enabled
        
    def initStatusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.sbLblConnectionState = QLabel()
        self.sbLblConnectionState.setText("Serial not connected")
        self.statusBar.addWidget(self.sbLblConnectionState)
        
        self.sbLblMeasurementState = QLabel()
        self.sbLblMeasurementState.setText("Measurement not running")
        self.statusBar.addWidget(self.sbLblMeasurementState)
        
        self.sbLblEps = QLabel()
        self.setEps(0)
        self.statusBar.addWidget(self.sbLblEps)
        
    def initMainToolbar(self):
        self.mainToolBar = QToolBar()
        self.addToolBar(self.mainToolBar)
        
        self.lblComPort = QtWidgets.QLabel()
        self.lblComPort.setObjectName("lblComPort")
        
        self.cmbComPort = QtWidgets.QComboBox()
        self.cmbComPort.setObjectName("cmbComPort")
        self.mainToolBar.addWidget(self.cmbComPort)
        
        self.btnConnect = QtWidgets.QPushButton()
        self.btnConnect.setObjectName("btnConnect")
        
        self.btnStartStop = QtWidgets.QPushButton()
        self.btnStartStop.setEnabled(False)
        self.btnStartStop.setObjectName("btnStartStop")
        
    def initUI(self):
        self.plotBV.setLabels(title="Bus voltage", left="Voltage [V]", bottom="time")
        self.plotBV.register("Bus voltage")
        self.plotBV.setClipToView(True)
        
        self.plotCA.setLabels(title="Current", left="Current [mA]", bottom="time")
        self.plotCA.setDownsampling(ds=4, auto=False, mode='peak')
        self.plotCA.setClipToView(True)
        self.plotCA.register("Current")
        
        
        self.plotPO.setLabels(title="Power", left="Power [mW]", bottom="time")
        self.plotPO.register("Power")
        self.plotPO.setClipToView(True)
        
        self.plotConsumption.setLabels(title="Consumption", left="Power [Wh]", bottom="time")
        self.plotConsumption.register("Consumption")
        self.plotConsumption.setClipToView(True)
        
        self.plotConsumptionMean.setLabels(title="Power Mean", left="Power [mW]", bottom="time")
        self.plotConsumptionMean.register("Power Mean")
        self.plotConsumptionMean.setClipToView(True)
        
        
        # menuBar
        
        self.actionBus_voltage.triggered.connect(self.menuBV)
        self.actionCurrent.triggered.connect(self.menuCA)
        self.actionPower.triggered.connect(self.menuPO)
        self.actionConsumption.triggered.connect(self.menuConsumption)
        self.actionMean_consumption.triggered.connect(self.menuConsumptionMean)
        
        # sidebar
        
        self.txtMaxPointsToDisplay.setText(str(self.maxPointsToDisplay))
        self.txtMaxPointsToDisplay.editingFinished.connect(self.txtMaxPointsToDisplayEdited)
        self.setMaxPointsToDisplay(self.maxPointsToDisplay)
        
        self.chkLimitMaxPointsToDisplay.toggled.connect(self.limitMaxPointsToDisplay)
        self.chkLimitMaxPointsToDisplay.setChecked(self.maxPointsToDisplayEnabled)
        self.limitMaxPointsToDisplay(self.maxPointsToDisplayEnabled)
        
        self.chkLinkXAxis.toggled.connect(self.linkXAxis)
        self.chkLinkXAxis.setChecked(self.linkXAxisValue)
        self.linkXAxis(self.linkXAxisValue)
        
        self.txtMaxPointsToStore.setText(str(self.maxPointsToStore))
        self.txtMaxPointsToStore.editingFinished.connect(self.txtMaxPointsToStoreEdited)
        
        self.chkLimitMaxPointsToStore.toggled.connect(self.limitMaxPointsToStore)
        self.chkLimitMaxPointsToStore.setChecked(self.maxPointsToStoreEnabled)
        self.limitMaxPointsToStore(self.maxPointsToStoreEnabled)
        
        self.chkAlwaysScrollToRight.toggled.connect(self.chkAlwaysScrollToRightToggled)
        
        self.btnResetXAxis.pressed.connect(self.btnResetXAxisPressed)
        self.btnResetYAxis.pressed.connect(self.btnResetYAxisPressed)
        
        self.btnConnect.pressed.connect(self.btnConnectPressed)        
        self.btnStartStop.pressed.connect(self.btnStartStopPressed)
        self.btnComReload.pressed.connect(self.initCmbComPorts)
        
        # sidebar: file
        self.chkSaveToFile.toggled.connect(self.chkSaveToFileToggled)
        self.btnChooseFile.pressed.connect(self.chooseFile)
        
    
    def updateCharts(self):
        self.plotBV.plot(x=self.xBV, y=self.yBV, clear=True)
        self.plotCA.plot(x=self.xBV, y=self.yCA, clear=True)
        self.plotPO.plot(x=self.xBV, y=self.yPO, clear=True)
        self.plotConsumption.plot(x=self.xBV, y=self.yConsumption, clear=True)
        self.plotConsumptionMean.plot(x=self.xBV, y=self.yConsumptionMean, clear=True)
        
        if self.maxPointsToDisplayEnabled:
            self.scrollToRight()
            
    def scrollToRight(self):
        if self.chkAlwaysScrollToRightEnabled:
            start = 0 if (len(self.xBV) - self.maxPointsToDisplay) <= 0 else len(self.xBV) - self.maxPointsToDisplay
            self.plotBV.setXRange(start, len(self.xBV))
            self.plotCA.setXRange(start, len(self.xBV))
            self.plotPO.setXRange(start, len(self.xBV))
            self.plotConsumption.setXRange(start, len(self.xBV))
            self.plotConsumptionMean.setXRange(start, len(self.xBV))
            
    def updateChartData(self):
        length = pm.data.qsize()
        
        for i in range(1, length):
            pv = pm.data.get()
            
            if self.maxPointsToStoreEnabled:
                while len(self.xBV) > self.maxPointsToStore:
                    self.xBV.pop(0)
                    self.yBV.pop(0)
                    self.yCA.pop(0)
                    self.yPO.pop(0)
                    self.yConsumption.pop(0)
                    self.yConsumptionMean.pop(0)
                
            self.yBV.append(pv.busvoltage)
            self.yCA.append(pv.current_ma)
            self.yPO.append(pv.power)
            
            self.yConsumptionAcc += ((pv.power * 0.001) / 3600 / 1000) # power in mW per ms
            self.yConsumption.append(self.yConsumptionAcc)
            
            self.yConspumtionCount += 1
            self.yPowerAcc += pv.power
            self.yConsumptionMean.append(self.yPowerAcc / self.yConspumtionCount)
            
            self.xCount += 1
            self.xBV.append(self.xCount)
                
            if self.chkSaveToFileEnabled == True and self.fileToSave is not None:
                self.fileToSave.write(str(pv.created) + ";" + str(pv.busvoltage)
                    + ";" + str(pv.current_ma) + ";" + str(pv.power) + "\n")
        
        
    def closeEvent(self, evt):
        pm.stopMeasurement()
        pm.stopThread()
        
        self.close()

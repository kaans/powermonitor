

class PlotsWidget(QWidget):
    
        
    def __init__(self):
        super().__init__()
        
        
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
        
        self.maxPointsToDisplay = 1000
        
        # init ui
        
        self.initUI()
        
        print("Plots widget initialized")
    
            
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
            
    def setMaxPointsToDisplay(self, max):
        self.maxPointsToDisplay = max
        
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
    
    
    def limitMaxPointsToDisplay(self, limit):
        self.maxPointsToDisplayEnabled = limit
        
        if limit:
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
            
            self.resetXAxis()
            
        self.scrollToRight()
        
    

        
    def resetXAxis(self):
        self.plotBV.enableAutoRange(axis=ViewBox.XAxis, enable=True)
        self.plotCA.enableAutoRange(axis=ViewBox.XAxis, enable=True)
        self.plotPO.enableAutoRange(axis=ViewBox.XAxis, enable=True)
        self.plotConsumption.enableAutoRange(axis=ViewBox.XAxis, enable=True)
        self.plotConsumptionMean.enableAutoRange(axis=ViewBox.XAxis, enable=True)

    def resetYAxis(self):
        self.plotBV.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        self.plotCA.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        self.plotPO.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        self.plotConsumption.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        self.plotConsumptionMean.enableAutoRange(axis=ViewBox.YAxis, enable=True)
        
        
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
            
    def updateChartData(self, data):
        
        for pv in data:
            
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

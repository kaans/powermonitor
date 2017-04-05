import glob
from queue import Queue
import sys
import threading
import time

from PyQt5.QtCore import QObject, pyqtSignal
import serial


print("Power Monitor 0.1")

class PowerValue:

    def __init__(self):
        self.busvoltage = 0
        self.current_ma = 0
        self.power = 0
        self.created = time.time()


class PowerMonitor(QObject):


    # signals
    thread_started = pyqtSignal()
    thread_stopped = pyqtSignal()
    
    measurement_started = pyqtSignal()
    measurement_stopped = pyqtSignal()
    
    events_per_second = pyqtSignal(float)
    

    def __init__(self):
        QObject.__init__(self)
        self.ser = None
        self.data = Queue()
        self.running = False
        self.measurementRunning = False
        self.countEvents = 0
        

    def listPorts(self):
        """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
    
    def startThread(self, port):
        if (not self.ser == None):
            # end old connection if available
            self.ser.close()
            
        self.ser = serial.Serial(port, 115200, timeout=1)
        
        self.thread = threading.Thread(target=self.run_internal)
        self.thread.start()
        
        self.thread_started.emit()
        
        self.running = True
    
    def run_internal(self):
        self.stop = False
        
        while (self.stop == False):
            buf = self.ser.readline()
            
            if len(buf) == 5:
                buf = buf[:4]
                if buf.decode('utf-8') == "SACK":
                    # start acknowledged
                    self.measurementRunning = True
                    self.measurement_started.emit()
                    
                elif buf.decode('utf-8') == "PACK":
                    # stop acknowledged
                    self.measurementRunning = False
                    self.measurement_stopped.emit()
                    
                    # reset count for next measurement
                    self.countEvents = 0
                    
            elif len(buf) == 8 and buf[0] == 68:
                # if line is a data line (D = 68)
                if self.countEvents == 0:
                    start = time.time()
                    
                self.countEvents += 1
                if self.countEvents % 1000 == 0:
                    diff = time.time() - start
                    eps = (self.countEvents / diff)
                    #print("eps: " + str(eps))
                    self.events_per_second.emit(eps)
                
                pv = PowerValue()
                
                pv.busvoltage = ((buf[1] << 8) | (buf[2])) * 0.001
                pv.current_ma = ((buf[3] << 8) | (buf[4])) / 10
                pv.power = ((buf[5] << 8) | (buf[6]))
                
                #print("{} V, {} mA, {} W".format(pv.busvoltage, pv.current_ma, pv.power))
                
                self.data.put(pv)
            elif len(buf) > 0:
                # no data received, print it
                print(buf)
                
                # only count times after data has been received
                if self.countEvents > 0:
                    self.countEvents += 1
                pass

        # wait until all outgoing data is sent
        self.ser.flush()
        
        while self.ser.out_waiting > 0:
            pass
        
        self.thread_stopped.emit()
        
        self.running = False
        self.ser.close()
    
    def isThreadRunning(self):
        return self.running
            
    def stopThread(self):
        self.stop = True

    def startMeasurement(self):
        if self.isThreadRunning():
            print("start mes")
            self.ser.write('S'.encode('utf-8')) # S
            self.ser.flush()

    def stopMeasurement(self):
        if self.isThreadRunning():
            print("stop mes")
            self.ser.write('P'.encode('utf-8')) # P
            self.ser.flush()
            self.measurementRunning = False
        
    def isMeasurementRunning(self):
        return self.measurementRunning
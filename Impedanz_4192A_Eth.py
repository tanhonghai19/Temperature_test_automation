import socket
import time
import numpy as np
import csv

IP_Addr = "169.254.80.115"
PORT = 1234
GPIB_Addr = "++addr 25\n"
CMD_Read_Value = "++read eoi\n"


class Impedance_Analyser:
    def __init__(self, ip, host):
        self.ip = ip
        self.host = host
        self.timeout = 3
        self.VISA_addr = GPIB_Addr
        self.MAX_NUM_POINTS = 500
        self.CMD_ID = "*IDN?\n"
        self.CMD_init = "ABW0A2T1F1\n"
        self.CMD_INIT = "ABW0A2T1F1C2\n"
        self.bDeviceInitialized = False

    def startComm(self):
        try:
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM,
                                        socket.IPPROTO_TCP)
            print ("socket created")
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip, self.host))
            print ("socket connected")
            return self.connect()
        except:
            print("startComm failed")
            time.sleep(1)
            return False

    def connect(self):
        self.socket.send(GPIB_Addr.encode("utf-8"))
        self.InitDevice()
        print("connected")
        return True

    def InitDevice(self):
        self.MAX_4192_LIMIT = 13000000.0
        self.MIN_4192_LIMIT = 5.0
        self.MAX_OSC_LEVEL = 1.1
        self.startFreq = self.MIN_4192_LIMIT
        self.endFreq = self.MAX_4192_LIMIT
        self.numPoints = self.MAX_NUM_POINTS
        # self.oscilation = self.MAX_OSC_LEVEL
        self.socket.send(self.CMD_init.encode("utf-8"))
        self.socket.send(self.CMD_INIT.encode("utf-8"))
        # self.setOscilation()

        self.bDeviceInitialized = True

    def getInfo(self):
        self.connect()
        self.socket.send(self.CMD_init.encode("utf-8"))
        self.socket.send(self.CMD_ID.encode("utf-8"))
        self.socket.send(CMD_Read_Value.encode("utf-8"))
        info = self.socket.recv(50)
        print(info)
        return info

    def setRange(self, startFreq, endFreq):
        if startFreq < 5.0:
            startFreq = 5.0
        else:
            startFreq = startFreq

        if endFreq > 13000000.0:
            endFreq = 13000000.0
        else:
            endFreq = endFreq

        # In order to use np.logspace
        self.startFreqLog = np.log10(startFreq)
        self.endFreqLog = np.log10(endFreq)

        # sweep frequency Range
        self.frequencyRange = np.logspace(self.startFreqLog, self.endFreqLog, num=self.MAX_NUM_POINTS)

    def setOscilation(self, oscilation):
        CMD_OSC = "OL%.03fEN\n" % oscilation
        self.socket.send(CMD_OSC.encode('utf-8'))

    def sweep_measure(self, start, end, set_osi):
        t_start = time.time()

        data = []

        self.setOscilation(set_osi)

        self.setRange(start, end)

        for x in np.nditer(self.frequencyRange):
            print(x)
            # write frequency
            currentFrequency = "FR%.6fEN\n" % (x / 1e3)
            self.socket.send(currentFrequency.encode("utf-8"))

            # Read display value
            self.socket.send(CMD_Read_Value.encode("utf-8"))
            displayValue = self.socket.recv(100)

            # read diaplay A
            realVal = float(displayValue[4:15])
            print("realVal: ", realVal)

            # read display B
            imgValue = float(displayValue[21:32])  # * (-1)
            print("imgValue: ", imgValue)

            # read display C
            if displayValue[34] == "K":
                freqValue = float(displayValue[36:-4])
            else:
                freqValue = float(displayValue[35:-4])
            print("freqValue: ", freqValue)

            data.append(["%.5e" % x, "%.5e" % realVal, "%.5e" % imgValue])

        t_end = time.time()
        t_run = t_end - t_start
        print(t_run)
        return data


if __name__ == "__main__":
    HP_4192A = Impedance_Analyser(IP_Addr, PORT)
    HP_4192A.startComm()
    HP_4192A.getInfo()

    with open("/home/pi/Desktop/test_result_ImpedanzAnalyzer.txt", "w") as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(HP_4192A.sweep_measure(5, 13000))



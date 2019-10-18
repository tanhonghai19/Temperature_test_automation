import socket
import time
import numpy as np
import csv

IP_addr = "169.254.80.115"
PORT = 1234
GPIB_Addr = "++addr 3\n"
CMD_Read = "++read eoi\n"


class SourceMeter:
    def __init__(self, ip, host):
        self.ip = ip
        self.host = host
        self.timeout = 2
        self.Channel = ""
        self.fVoltage = float(0)
        self.fMeasuredVoltage = float(0)
        self.fMeasuredCurrent = float(0)
        self.bChannelInitialized = False
        self.bDeviceInitialized = False
        self.CMD_ID = "*IDN?\n"

    def reset(self):
        self.Channel = " "
        self.fVoltage = float(0)
        self.fMeasuredVoltage = float(0)
        self.fMeasuredCurrent = float(0)
        self.bChannelInitialized = False
        self.setV("a", 0)
        self.bChannelInitialized = False
        self.setV("b", 0)
        self.bChannelInitialized = False
        self.Channel = " "

    def GoSafe(self):
        self.reset()

    def setChannel(self, ch):
        if ch == "a" or ch == "A":
            self.Channel = "a"
        else:
            self.Channel = "b"

        self.CMD_Function = "smu" + self.Channel + ".source.func = smu" + self.Channel + ".OUTPUT_DCVOLTS\n"
        self.CMD_VoltageSet = "smu" + self.Channel + ".source.levelv = "
        self.CMD_ChannelON = "smu" + self.Channel + ".source.output = smu" + self.Channel + ".OUTPUT_ON\n"
        self.CMD_Read_I = "print(smu" + self.Channel + ".measure.i())\n"
        self.CMD_Read_V = "print(smu" + self.Channel + ".measure.v())\n"
        self.CMD_Read_R = "print(smu" + self.Channel + ".measure.r())\n"

    def startComm(self):
        try:
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM,
                                        socket.IPPROTO_TCP)
            print ("socket created")
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip, self.host))
            #print ("connected")
            #self.getR()
            return self.connect()
        except:
            print("startComm failed")
            time.sleep(1)
            return False

    def connect(self):
        if (self.bDeviceInitialized == False):
            self.socket.send(GPIB_Addr.encode("utf-8"))
            self.bDeviceInitialized = True
            print("connected")

    # Write intialize for DC voltage
    def InitChannel(self):
        self.connect()
        if (self.bChannelInitialized == False):
            self.socket.send(self.CMD_Function.encode("utf-8"))
            self.bChannelInitialized = True
            print("channel initialized")

    # Write desired voltage
    def setV(self, ch, v):
        self.fVoltage = v
        self.setChannel(ch)
        self.InitChannel()
        self.socket.send((self.CMD_VoltageSet + str(self.fVoltage) + "\n").encode("utf-8"))
        self.socket.send(self.CMD_ChannelON.encode('utf-8'))

    # Command to read current and voltage
    def Measure(self, ch, V_start, V_end, V_step):
        data = []
        t_start = time.time()
        dataNum = np.arange(V_start, V_end, V_step)
        it = np.nditer(dataNum)
        for x in it:
            if abs(x) > 0:
                self.setV(ch, x)

                # read current
                self.socket.send(self.CMD_Read_I.encode("utf-8"))
                self.socket.send(CMD_Read.encode("utf-8"))
                fMeasuredCurrent = float(self.socket.recv(50))
                print("Current: ", fMeasuredCurrent)

                # read voltage
                self.socket.send(self.CMD_Read_V.encode("utf-8"))
                self.socket.send(CMD_Read.encode("utf-8"))
                fMeasuredVoltage = float(self.socket.recv(50))
                print("Voltage: ", fMeasuredVoltage)

                # read resistance
                self.socket.send(self.CMD_Read_R.encode("utf-8"))
                self.socket.send(CMD_Read.encode("utf-8"))
                fMeasuredresistance = float(self.socket.recv(50))
                print("Resistance: ", fMeasuredresistance)

                # calculate resistance
                self.resistanceR = fMeasuredVoltage / fMeasuredCurrent
                print("Resistance: ", self.resistanceR)

                # update data on the screen
                # Father.updateSweep([fMeasuredCurrent, fMeasuredVoltage, resistanceR])

                # data storage
                data.append(["%f" % fMeasuredVoltage, "%f" % fMeasuredCurrent, "%f" % fMeasuredresistance, "%f" % self.resistanceR])
                # time.sleep(1)

        t_end = time.time()
        t_run = t_end - t_start
        print(t_run)
        return data

    def getInfo(self):
        self.connect()
        self.socket.send(self.CMD_ID.encode("utf-8"))
        self.socket.send(CMD_Read.encode("utf-8"))
        info = self.socket.recv(1024)
        print(info)
        return info


if __name__ == "__main__":
    SM = SourceMeter(IP_addr, PORT)
    SM.startComm()
    with open("D:/test_result_Sourcemeter.txt", "w") as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(SM.Measure("a", -40, 40, 0.1))

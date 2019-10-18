import socket
import time

IP_addr = "169.254.80.115"
PORT = 1234
GPIB_Addr = "++addr 03\n"
CMD_Read = "++read eoi\n"


class SourceMeter:
    def __init__(self, ip, host):
        self.ip = ip
        self.host = host
        self.timeout = 5
        self.Channel = " "
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

    def startComm(self):
        try:
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM,
                                        socket.IPPROTO_TCP)
            print ("socket created")
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip, self.host))
            print ("socket connected")
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
        self.fVoltage = str(v)
        self.setChannel(ch)
        self.InitChannel()
        self.socket.send((self.CMD_VoltageSet + self.fVoltage + "\n").encode("utf-8"))
        self.socket.send(self.CMD_ChannelON.encode("utf-8"))

    # Command to read current and voltage
    def Measure(self, ch, v):
        self.setV(ch, v)
        self.socket.send(self.CMD_Read_I.encode("utf-8"))
        self.socket.send(CMD_Read.encode("utf-8"))
        self.fMeasuredCurrent = self.socket.recv(50)
        print("Current: ", float(self.fMeasuredCurrent))

        self.socket.send(self.CMD_Read_V.encode("utf-8"))
        self.socket.send(CMD_Read.encode("utf-8"))
        fMeasuredVoltage = float(self.socket.recv(50))
        print("Voltage: ", fMeasuredVoltage)

        resistanceR = fMeasuredVoltage / float(self.fMeasuredCurrent)
        print ("Resistance: ", resistanceR)
        return self.fMeasuredCurrent

    def getInfo(self):
        self.connect()
        self.socket.send(self.CMD_ID.encode("utf-8"))
        self.socket.send(CMD_Read.encode("utf-8"))
        info = self.socket.recv(30)
        print(info)
        #return info

    def getV(self):
        return self.fMeasuredVoltage

    def getI(self):
        return self.fMeasuredCurrent

    def getR(self):
        return self.fMeasuredVoltage / self.fMeasuredCurrent

    def __str__(self):
        return "V = %f" % self.getV() + " I = %E" % self.getI() + " R = %f" % self.getR()


if __name__ == "__main__":
    SM = SourceMeter(IP_addr, PORT)
    SM.startComm()
    #SM.getInfo()
    while True:
        SM.Measure("a", 5)
        time.sleep(1)

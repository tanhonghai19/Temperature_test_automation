import socket
import time

IP_Addr = "169.254.101.115"
PORT = 1234
GPIB_Addr = "+addr 17\n"
CMD_Read_Value = "++read eoi\n"


class LCR_Meter:
    def __init__(self, ip, host):
        self.ip = ip
        self.host = host
        self.timeout = 5
        self.VISA_addr = GPIB_Addr
        self.fVoltage = float(0)
        self.fFrequency = float(0)
        self.dataCPRP = float(0)
        self.dataRX = float(0)
        self.CMD_ID = "*IDN?\n"
        # self.CMD_VOLTAGE = "VOLT 2 V\n"
        # self.CMD_FREQ = "FREQ 2 KHZ\n"
        self.CMD_READ = "FETC?\n"
        self.CMD_FUNCTION_CPRP = "FUNC:IMP CPRP\n"
        self.CMD_FUNCTION_RX = "FUNC:IMP RX\n"
        self.bDeviceInitialized = False
        self.instLCR = ""
        self.rm = ""

    def reset(self):
        self.fVoltage = float(0)
        self.fFrequency = float(0)

    def GoSafe(self):
        self.reset()

    def startComm(self):
        try:
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM,
                                        socket.IPPROTO_TCP)
            print ("socket created")
            self.socket.settimeout(self.timeout)
            print("timeout set")
            self.socket.connect((self.ip, self.host))
            print ("connected")
            #self.getR()
            return self.connect_device()
        except:
            print('startComm failed')
            time.sleep(1)
            return False

    def connect_device(self):
        if (self.bDeviceInitialized == False):
            self.socket.send(GPIB_Addr.encode("utf-8"))
            self.bDeviceInitialized = True
            print("connected")
            return True

    def getInfo(self):
        self.connect_device()
        self.socket.send(self.CMD_ID.encode("utf-8"))
        self.socket.send(CMD_Read_Value.encode("utf-8"))
        data = self.socket.recv(1024)
        print(data)
        return data

    def setV(self, VOLT):
        CMD_VOLTAGE = "VOLT %f V\n" % float(VOLT)
        self.socket.send(CMD_VOLTAGE.encode("utf-8"))
        #print("Voltage set")

    def setFREQ(self,freq):
        CMD_FREQ = "FREQ %d KHZ\n" % int(freq)
        self.socket.send(CMD_FREQ.encode("utf-8"))
        #print("Frequency set")

    def measure(self, setV, setF):
        data = []
        self.VOLT = setV
        self.FREQ = setF
        self.setV(self.VOLT)
        self.setFREQ(self.FREQ)

        # read CPRP value
        self.socket.send(self.CMD_FUNCTION_CPRP.encode("utf-8"))
        time.sleep(0.3)
        self.socket.send(self.CMD_READ.encode("utf-8"))
        self.socket.send(CMD_Read_Value.encode("utf-8"))
        dataCPRP = self.socket.recv(50)
        str_CPRP = (dataCPRP.decode()).strip()
        list_CPRP = str_CPRP.split(",")
        CP = list_CPRP[0]
        RP = list_CPRP[1]

        # read RX value
        self.socket.send(self.CMD_FUNCTION_RX.encode("utf-8"))
        time.sleep(0.3)
        self.socket.send(self.CMD_READ.encode("utf-8"))
        self.socket.send(CMD_Read_Value.encode("utf-8"))
        dataRX = self.socket.recv(50)
        str_RX = (dataRX.decode()).strip()
        list_RX = str_RX.split(",")
        R = list_RX[0]
        X = list_RX[1]

        data.append((CP, RP, R, X))
        # print(data)
        return data



if __name__ == "__main__":
    LCR = LCR_Meter(IP_Addr, PORT)
    LCR.startComm()
    # LCR.getInfo()
    with open("D:/test_result.txt", "w") as file:
        for i in range(1000):
            file.writelines(LCR.measure(1.1, 1300000) + "\n")
            time.sleep(0.1)


import socket
import time

IP_Addr = "169.254.80.115"
PORT = 1234
timeout = 2
GPIB_Addr = "++addr 26\n"
R_Mode = "F2R0X;\n"
CMD_Read = "++read eoi\n"

DMM_RESET = 0
DMM_DISCONNECTED = 1
DMM_CONNECTED = 2
DMM_RETRY_CONNECTION = 5


class DMM_196:
    def __init__(self, ip, host):
        self.ip = ip
        self.host = host
        self.state = DMM_RESET
        self.timeout = timeout

    def setState(self, state_prm):
        self.state = state_prm

    def IsConnected(self):
        self.state_machine()
        for i in range(DMM_RETRY_CONNECTION):
            if( self.state != DMM_CONNECTED ):
                self.state_machine()
                time.sleep(1)
            else:
                break

        return (self.state == DMM_CONNECTED)

    def state_machine(self):
        if self.state == DMM_RESET:
            self.fVal = 0
            self.state = DMM_DISCONNECTED
            print("DMM196: RESET_STATE")
        elif self.state == DMM_DISCONNECTED:
            print("DMM196: DISCONNECTED_STATE")
            ret = self.startComm()
            if ret == True:
                self.state = DMM_CONNECTED
            else:
                self.state = DMM_DISCONNECTED
        elif self.state == DMM_CONNECTED:
            print("DMM196: CONNECTED_STATE")

    def startComm(self):
        try:
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM,
                                        socket.IPPROTO_TCP)
            print("socket created")
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip, self.host))
            print("connected")
            #self.getR()
            return self.connect()
        except:
            print("startComm failed")
            time.sleep(1)
            return False

    def getR(self):
        self.socket.send(CMD_Read.encode("utf-8"))
        data = self.socket.recv(30)
        R_value = (data[5:-2]).decode()
        R = R_value[:7] + R_value[8:]
        if len(R) < 2:
            R = "-1"
        return R

    def connect(self):
        self.socket.send(GPIB_Addr.encode("utf-8"))
        self.socket.send(R_Mode.encode("utf-8"))
        return True

    def read_resiatance(self):
        try:
            return self.getR()
        except:
            print("Connection failed")
            self.setState(DMM_DISCONNECTED)
            if(self.IsConnected()):
                return self.getR()
            else:
                return str(-1)


if __name__ == "__main__":
    DMM = DMM_196(IP_Addr, PORT)
    DMM.startComm()
    for i in range(30000):
        print("Measured resistance %d: " % (i+1) + DMM.read_resiatance())
        # op = open("D:/ballon3.txt", "a")
        # op.write( DMM.read_resiatance() +"\n")
        # op.close()
        time.sleep(0.5)

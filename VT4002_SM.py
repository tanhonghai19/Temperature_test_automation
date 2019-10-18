import visa
from time import sleep
import time


IP_Addr = "169.254.80.96"
timeout = 2

VT4002_RESET = 0
VT4002_DISCONNECTED = 1
VT4002_CONNECTED = 2
VT4002_RETRY_CONNECTION = 5


class VT4002:
    def __init__(self, ip):
        self.ip = IP_Addr
        self.state = VT4002_RESET
        self.timeout = timeout

    def setState(self, state_prm):
        self.state = state_prm

    def IsConnected(self):
        self.state_machine()
        for i in range(VT4002_RETRY_CONNECTION):
            if self.state != VT4002_CONNECTED:
                self.state_machine()
                time.sleep(1)
            else:
                break

        return self.state == VT4002_CONNECTED

    def state_machine(self):
        if self.state == VT4002_RESET:
            self.fVal = 0
            self.state = VT4002_DISCONNECTED
            print("VT: RESET_STATE")
        elif self.state == VT4002_DISCONNECTED:
            print("VT: DISCONNECTED_STATE")
            ret = self.startComm()
            if ret == True:
                self.state = VT4002_CONNECTED
            else:
                self.state = VT4002_DISCONNECTED
        elif self.state == VT4002_CONNECTED:
            print("VT: CONNECTED_STATE")

    def startComm(self):
        try:
            self.address = "TCPIP0::" + self.ip + "::2049::SOCKET"
            self.resourceManager = visa.ResourceManager("@py")
            self.instance = self.resourceManager.open_resource(self.address, read_termination="\r")
        except:
            time.sleep(1)
            return False

    def close(self):
        if self.instance is not None:
            self.instance.write("$01E 0025.0 00\r")
            self.instance.close()
            self.instance = None

    def write_temp(self, set_temp):
        #print('Set new Temperature: %f' % set_temp)
        string_temp = "{:.1f}".format(set_temp)
        string_temp = string_temp.zfill(6)
        string_cmd = "$01E " + string_temp + " 01\r"
        #print(string_cmd)
        self.instance.write(string_cmd)

    def set_temp(self,set_temp):
        try:
            return self.write_temp(set_temp)
        except:
            print("Connection failed")
            self.setState( VT4002_DISCONNECTED )
            if self.IsConnected():
                return self.write_temp(set_temp)
            else:
                return str(-1)

    def get_temp(self):
        real_temp = ""
        while len(real_temp) == 0:
            self.temp = self.instance.query_ascii_values("$01I\r", converter="s", separator=" ")
            set_temp = self.temp[0]
            real_temp = self.temp[1]
            if len(real_temp) == 0:
                sleep(0.03)
                continue
            return [float(set_temp), float(real_temp)]

    def read_temp(self):
        try:
            return self.get_temp()
        except:
            print("Connection failed")
            self.setState(VT4002_DISCONNECTED)
            if self.IsConnected():
                return self.get_temp()
            else:
                return str(-1)


if __name__ == "__main__":
    Oven = VT4002(IP_Addr)
    Oven.startComm()
    Oven.set_temp(25)


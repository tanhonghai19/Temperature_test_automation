import serial
from struct import *
from time import sleep
from django.utils.encoding import smart_str, smart_unicode


NX_SERIAL_BAUD = 9600
#command1 = "page 3\xff\xff\xff"
#command = "get n123.val\xff\xff\xff"
command = "get n0.val\xff\xff\xff"
NX_SERIAL_PORT = "/dev/ttyUSB0"
#NX_SERIAL_PORT = "COM7"

class Nextion:
    def __init__(self, serial_port):
        self.ser = serial.Serial(serial_port, NX_SERIAL_BAUD, timeout=0.2, parity=serial.PARITY_NONE, stopbits=1, bytesize=8)

    def get_val(self, cmd):
        #print(smart_str(cmd))
        self.ser.write(smart_str(cmd))
        r = self.ser.read_until(terminator="\xff\xff\xff")
        #print(r)
        if len(r) > 5:
            rclean = r[1:-3]
        elif len(r) < 4:
            r = self.ser.read_until(terminator="\xff\xff\xff")
            rclean = r[1:-3]
        else:
            rclean = r[1:]

        print(rclean)
        return unpack("l", rclean)[0]

    def read(self):
        read_val = self.ser.readlines()
        return read_val

    def write(self, cm):
        self.ser.write(smart_str(cm))


def main():
    DIS = Nextion(NX_SERIAL_PORT)
    RETURN_VAL = set()

    while True:
        DEVICE = str(DIS.read())
        RETURN_VAL.add(DEVICE)
        print(RETURN_VAL)
        sleep(1)


if __name__ == "__main__":
    main()

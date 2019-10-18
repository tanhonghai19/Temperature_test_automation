import sys
sys.path.append('/home/pi/Desktop/py/')
import VT4002_SM
import os
import write_display
import time

VT4002_IP = "169.254.80.96"
NX_SERIAL_PORT = "/dev/ttyUSB0"

DIS = write_display.Nextion(NX_SERIAL_PORT)


class VT_Manual:
    def main(self,set_temp, Father):
        self.set_temp = set_temp
        t_start = time.time()
        print("start")
        print(self.set_temp)

        OVEN = VT4002_SM.VT4002(VT4002_IP)
        OVEN.startComm()
        RE_VAL = set()

        while True:
            t_now = time.time()
            t_run = t_now - t_start
            # setting the oven
            OVEN.set_temp(self.set_temp)

            # run oven
            print('01 - Reading data from Oven...')

            temp = OVEN.read_temp()
            temp_set = str(format(temp[0], "0,.2f"))
            temp_real = str(format(temp[1], "0,.2f"))

            Father.updateOven([str(t_run), str(self.set_temp), temp_real])

            DE = str(DIS.read())
            # print (DE)
            RE_VAL.add(DE)
            # print (RE_VAL)

            if "['e\\x11\\x04\\x01\\xff\\xff\\xff']" in RE_VAL:
                print("Exiting")
                OVEN.close()
                RE_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")
                return

            elif "['e\\x11\\x05\\x01\\xff\\xff\\xff']" in RE_VAL:
                # DIS.write("rest\xff\xff\xff")
                RE_VAL.clear()
                DIS.write("page restart\xff\xff\xff")
                os.system("sudo reboot")

            print('07 - Updating Display...')

            time.sleep(1)


if __name__ == "__main__":
    PID_VT = VT_Manual()
    PID_VT.main(30, None)

import sys
sys.path.append('/home/pi/Desktop/py/')
import TTC4006_Tira
import datetime
import time
import write_display
import os

TTC_SERIAL_PORT = '/dev/ttyUSB1'
TTC_SERIAL_BAUD = 19200
TTC_ADDRESS = 17

NX_SERIAL_PORT = "/dev/ttyUSB0"

DIS = write_display.Nextion(NX_SERIAL_PORT)


class TTC_Manual:
    def main(self, set_temp, Father):
        RE_VAL = set()

        self.set_temp = set_temp
        t_start = time.time()
        print("start")
        print(self.set_temp)

        OVEN = TTC4006_Tira.TTC4006(TTC_SERIAL_PORT)
        OVEN.TTC_ON()
        OVEN.TTC_ENABLE_TEMP()

        while True:
            t_now = time.time()
            t_run = t_now - t_start
            # setting the oven
            OVEN.TTC_Set_Temp(self.set_temp)

            # run oven
            print('01 - Reading data from Oven...')

            temp_set = str(format(OVEN.TTC_Read_SP_Temp(), "0,.2f"))
            temp_real = str(format(OVEN.TTC_Read_PV_Temp(), "0,.2f"))

            Father.updateOven([str(t_run), str(self.set_temp), temp_real])

            DE = str(DIS.read())
            # print (DE)
            RE_VAL.add(DE)
            # print (RE_VAL)

            if "['e\\x11\\x04\\x01\\xff\\xff\\xff']" in RE_VAL:
                print("Exiting")
                OVEN.TTC_OFF()
                RE_VAL.clear()
                DIS.write("page Device Select\xff\xff\xff")
                return

            elif "['e\\x11\\x05\\x01\\xff\\xff\\xff']" in RE_VAL:
                # DIS.write("rest\xff\xff\xff")
                RE_VAL.clear()
                DIS.write("page restart\xff\xff\xff")
                os.system("sudo reboot")

            time.sleep(1)


if __name__ == "__main__":
    PID_VT = TTC_Manual()
    PID_VT.main(25, None)

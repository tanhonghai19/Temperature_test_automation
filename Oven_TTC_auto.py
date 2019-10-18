import sys
sys.path.append('/home/pi/Desktop/py/')
import TTC4006_Tira
from TempProfile import readTempProfile
import datetime
import time
import write_display
import os

folder = "/media/pi/"
TTC_SERIAL_PORT = '/dev/ttyUSB1'
TTC_SERIAL_BAUD = 19200
TTC_ADDRESS = 17

FILE_NAME = "/home/pi/Desktop/Temperature_profile.txt"

NX_SERIAL_PORT = "/dev/ttyUSB0"

DIS = write_display.Nextion(NX_SERIAL_PORT)


class TTC_Auto:
    def main(self, Father):
        RE_VAL = set()
        print("start")
        TP = readTempProfile(FILE_NAME)[0]
        print(TP)

        OVEN = TTC4006_Tira.TTC4006(TTC_SERIAL_PORT)
        OVEN.TTC_ON()
        OVEN.TTC_ENABLE_TEMP()

        t_start = time.time()

        for step in TP:
            # setting the oven
            step_time = step[0] * 60  # step_time in seconds
            step_temp = float(format(float(step[1]), ".2f"))

            print(step)

            t1 = datetime.datetime.now()
            t2 = datetime.datetime.now() + datetime.timedelta(seconds=step_time)

            while (t1 < t2):
                # run oven
                print('01 - Reading data from Oven...')

                t_step = time.time()
                t_r = t_step - t_start
                t_run = format(t_r, "0.2f")

                temp_set1 = OVEN.TTC_Read_SP_Temp()
                temp_real1 = OVEN.TTC_Read_PV_Temp()
                temp_set = str(format(temp_set1, "0,.2f"))
                temp_real = str(format(temp_real1, "0,.2f"))

                OVEN.TTC_Set_Temp(step_temp)

                Father.updateOven([str(t_run), str(step_temp), temp_real])

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

                t1 = datetime.datetime.now()


if __name__ == "__main__":
    PID_VT = TTC_Auto()
    PID_VT.main(None)

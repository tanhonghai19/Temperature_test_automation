import sys
sys.path.append('/home/pi/Desktop/py/')
import VT4002_SM
from TempProfile import readTempProfile
import datetime
import time
import write_display
import os

folder = "/media/pi/"
VT4002_IP = "169.254.80.96"

FILE_NAME = "/home/pi/Desktop/Temperature_profile.txt"

NX_SERIAL_PORT = "/dev/ttyUSB0"

DIS = write_display.Nextion(NX_SERIAL_PORT)


class VT_Auto:
    def main(self, Father):
        RE_VAL = set()

        print("start")
        TP = readTempProfile(FILE_NAME)[0]
        print(TP)

        OVEN = VT4002_SM.VT4002(VT4002_IP)
        OVEN.startComm()

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

                temp = OVEN.read_temp()
                temp_set = temp[0]
                temp_real = temp[1]

                OVEN.set_temp(step_temp)

                Father.updateOven([str(t_run), str(step_temp), temp_real])

                DE = str(DIS.read())
                print(DE)
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

                time.sleep(1)

                t1 = datetime.datetime.now()


if __name__ == "__main__":
    PID_VT = VT_Auto()
    PID_VT.main(None)

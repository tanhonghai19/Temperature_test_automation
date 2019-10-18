import relay
from time import sleep
import time
import write_display
import os

NX_SERIAL_PORT = "/dev/ttyUSB0"

DIS = write_display.Nextion(NX_SERIAL_PORT)


class Relay_mode:
    def main(self, num, interval, Father):
        RE_VAL = set()
        t_start = time.time()
        self.num = num
        self.interval = interval
        REL = relay.Relay_module()
        REL.reset()
        while True:
            for i in range(num):
                t_now = time.time()
                t_run = t_now - t_start
                REL.RelaySelect(i)
                print(i)
                sleep(interval)
                REL.RelayDeSelect(i)

                Father.updateRelay([str(t_run), i, ])

                DE = str(DIS.read())
                # print (DE)
                RE_VAL.add(DE)
                # print (RE_VAL)

                if "['e\\x10\\x02\\x01\\xff\\xff\\xff']" in RE_VAL:
                    print("Exiting")
                    RE_VAL.clear()
                    DIS.write("page Device Select\xff\xff\xff")
                    return

                elif "['e\\x10\\x01\\x01\\xff\\xff\\xff']" in RE_VAL:
                    # DIS.write("rest\xff\xff\xff")
                    RE_VAL.clear()
                    DIS.write("page restart\xff\xff\xff")
                    os.system("sudo reboot")

                print('07 - Updating Display...')


if __name__ == "__main__":
    mode = Relay_mode()
    mode.main(8, 2, None)

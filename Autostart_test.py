import write_display
from time import sleep

command = 'get n0.val\xff\xff\xff'
NX_SERIAL_PORT = "/dev/ttyUSB0"

def main():
    sleep(20)

    NX = write_display.Nextion(NX_SERIAL_PORT)
    for i in range(1000):
        print (i)
        cmd = 'n123.val=' + str(i) + '\xff\xff\xff'
        # cmd = 'n0.val=' + str(i) + '\xff\xff\xff'
        NX.write(cmd)
        # print(NX.get_val(command))
        sleep(0.01)


if __name__ == '__main__':
    main()




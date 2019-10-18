import minimalmodbus
import serial
from time import sleep

TTC_SERIAL_PORT = "/dev/ttyUSB1" #'COM3'
TTC_SERIAL_BAUD = 19200
TTC_ADDRESS = 17


class TTC4006:
    def __init__(self, serial_port):
        self.instrument = minimalmodbus.Instrument(serial_port, TTC_ADDRESS)  # port name, slave address (in decimal)
        self.instrument.serial.baudrate = 19200  # Baud
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = serial.PARITY_NONE
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1  # seconds
        self.instrument.mode = minimalmodbus.MODE_RTU  # rtu or ascii mode
        return

    def TTC_ENABLE_TEMP(self):
        self.instrument.write_register(2300, 0b0000000100000011 )
        return

    def TTC_ON(self):
        self.instrument.write_register(2300, 0b0000000000000011)
        return

    def TTC_OFF(self):
        self.instrument.write_register(2300, 0b0000000000000000)
        return

    def TTC_Set_Temp(self, sp_temp):
        if sp_temp < 0:
            self.instrument.write_register(2304, 655.36-abs(sp_temp), signed=False, numberOfDecimals=2)
            self.instrument.write_register(2305, 655.35, signed=False, numberOfDecimals=2)
            self.instrument.write_register(2306, int(10.00 * 100))
        else:
            sp_temp_w = sp_temp
            self.instrument.write_register(2304, sp_temp_w, numberOfDecimals=2)
            self.instrument.write_register(2305, 0, signed=False, numberOfDecimals=2)
            self.instrument.write_register(2306, int(10.00 * 100))
        return

    def TTC_Read_PV_Temp(self):
        reg = self.instrument.read_registers(2000, 1)
        val = reg[0]
        if val > 2 ** 15:
            val_with_signal = - (2 ** 16 - val)
        else:
            val_with_signal = val
        return float(val_with_signal) * (1e-2)

    def TTC_Read_SP_Temp(self):
        reg = self.instrument.read_registers(2064, 1)
        #print ("reg =", reg)
        val = reg[0]
       # print ("val =", val)
        if val > 2 ** 15:
            val_with_signal = - (2 ** 16 - val)
        else:
            val_with_signal = val
        return float(val_with_signal) * (1e-2)


def main():
    # Connecting to OVEN
    print("Connecting to Oven in: " + TTC_SERIAL_PORT)
    ser = TTC4006( TTC_SERIAL_PORT)

    # Run the Oven
    # print("Turn ON Oven")
    ser.TTC_ON()
    ser.TTC_ENABLE_TEMP()
    ser.TTC_Set_Temp(25)

    # Check Oven Temperature each 20s for 10 times
    for i in range(1000):
        rd_SP_Temp = ser.TTC_Read_SP_Temp()
        rdtemp = ser.TTC_Read_PV_Temp()
        print("SP Temp: [%0.2f oC]" % rd_SP_Temp + " - PV Temp: [%0.2f oC]" % rdtemp)
        sleep(0.5)

    ser.TTC_OFF()
    return


if __name__ == "__main__":
    main()

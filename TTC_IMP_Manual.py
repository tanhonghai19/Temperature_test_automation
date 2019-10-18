import sys

sys.path.append("/home/pi/Desktop/py/")
from time import sleep
import datetime
import TTC4006_Tira
import Impedanz_4192A_Eth
import bme280
import time
import detect_file
import relay
import write_display
import os
import data_storage
import PID

# FILE_NAME = "/media/pi/B49E-19751/Temperature_profile.txt"
folder = "/media/pi/"
TTC_SERIAL_PORT = "/dev/ttyUSB1"
TTC_SERIAL_BAUD = 19200
TTC_ADDRESS = 17
IMP_IP = "169.254.80.115"
IMP_PORT = 1234
NX_SERIAL_PORT = "/dev/ttyUSB0"  # COM7
I2C_address = 0x76

DIS = write_display.Nextion(NX_SERIAL_PORT)

command_sample = 'get n123.val\xff\xff\xff'

APP_OVEN_PRESENT = True
APP_IMP_PRESENT = True
APP_BME_280_PRESENT = True
APP_NEXTION_PRESENT = True
APP_PEN_DRIVE = True

# HUMIDITY SENSOR PARAMETERS
BME_280_INVALID_TEMP = -273
BME_280_INVALID_HUMI = -273

# RELAY PARAMETERS
RELAY_HOLDING_TIME = 1.94


class TTC_IMP_Manual:
    def main(self, num_samples, set_temperature, start_freq, end_freq, set_voltage, Father):
        RE_VAL = set()

        # Initialize Relay
        REL = relay.Relay_module()
        REL.reset()

        # set PID parameters
        P = 5
        I = 0
        D = 0

        pid = PID.PID(P, I, D)
        pid.setSampleTime(1)

        self.NEXTION_NUM_SAMPLES = num_samples
        self.NEXTION_SET_TEMP = float(format(float(set_temperature) / 0.84, ".2f"))
        self.NEXTION_START_FREQ = start_freq
        self.NEXTION_END_FREQ = end_freq
        self.NEXTION_SET_VOLTAGE = set_voltage

        # import oven and multimeter
        if APP_OVEN_PRESENT:
            OVEN = TTC4006_Tira.TTC4006(TTC_SERIAL_PORT)
            OVEN.TTC_ON()
            OVEN.TTC_ENABLE_TEMP()

        if APP_IMP_PRESENT:
            IMP = Impedanz_4192A_Eth.Impedance_Analyser(IMP_IP, IMP_PORT)
            IMP.startComm()

        # create file and title
        CF = data_storage.create_file()
        test_mode = "Auto"
        equipment_Info = "TTC-4006 + IMP-4192A"
        Driver_root = detect_file.File(folder)[1]
        start_time = str(datetime.datetime.now())
        filename = start_time.replace(" ", "_").replace(".", "-").replace(":", "-")
        CF.folder(Driver_root, filename)

        t_start = time.time()

        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now() + datetime.timedelta(seconds=20 * 60)

        while True:
            if APP_OVEN_PRESENT:
                # run oven)
                print("01 - Reading data from Oven...")
                temp_real = OVEN.TTC_Read_PV_Temp()
                temp_set = OVEN.TTC_Read_SP_Temp()
            else:
                temp_set = format(1.00, "0.2f")
                temp_real = format(1.00, "0.2f")

            pid.SetPoint = self.NEXTION_SET_TEMP
            pid.setKp(float(P))
            pid.setKi(float(I))
            pid.setKd(float(D))

            # read temperature sensor
            # Humidity Sensor
            # If is not OK => apply non valid temp and humidity
            print("02 - Reading data from Humidity Sensor...")
            if APP_BME_280_PRESENT:
                try:
                    temperature, pressure, humidity = bme280.readBME280All()

                    # Medicine
                    if ((humidity == None) or (temperature == None)):
                        humidity = BME_280_INVALID_HUMI
                        temperature = BME_280_INVALID_TEMP
                        print("02 - Reading data from Humidity Sensor (NONE! - ERROR)...")
                    elif ((type(humidity) == str) or (type(temperature) == str)):
                        humidity = BME_280_INVALID_HUMI
                        temperature = BME_280_INVALID_TEMP
                        print("02 - Reading data from Humidity Sensor (INVALID STRING! - ERROR)...")

                except:
                    humidity = BME_280_INVALID_HUMI
                    temperature = BME_280_INVALID_TEMP
                    print("02 - Reading data from Humidity Sensor (INVALID STRING! - ERROR)...")

            else:
                print("02 - Reading data from Humidity Sensor (DISABLED)...")
                humidity = BME_280_INVALID_HUMI
                temperature = BME_280_INVALID_TEMP

            HUMI_sensor = format(humidity, "0.2f")
            TEMP_sensor = format(temperature, "0.2f")
            print('02 - Reading data from Humidity Sensor: Temp(oC): ', TEMP_sensor)
            print('02 - Reading data from Humidity Sensor: Humi(%): ', HUMI_sensor)

            print("Sensor Temperature : ", str(TEMP_sensor))

            pid.update(float(TEMP_sensor))

            target_temperature = pid.output

            if target_temperature > 130:
                target_temperature = 130
            elif target_temperature < -40:
                target_temperature = -40
            else:
                target_temperature = target_temperature

            print("PID set Temperature : ", str(target_temperature))
            print("Chamber real Temperature : ", temp_real)

            OVEN.TTC_Set_Temp(target_temperature)

            t_step = time.time()
            while (t1 > t2):
                for i in range(self.NEXTION_NUM_SAMPLES):
                    # run time
                    t_run = format(t_step - t_start, "0.2f")

                    # relay selection
                    print("03 - Swtich Relay: %d" % i)
                    REL.RelaySelect(i)
                    sleep(RELAY_HOLDING_TIME)

                    # create folder for each sample
                    current_time = str(datetime.datetime.now())
                    self.time_str = current_time.replace(" ", "_").replace(".", "-").replace(":", "-")

                    Father.updateIMPSweep([temp_set, temp_real, TEMP_sensor, HUMI_sensor, t_run, "Measureing", " ", i])

                    DE = str(DIS.read())
                    # print (DE)
                    RE_VAL.add(DE)
                    # print (RE_VAL)

                    if "['e\\x0f\\x1b\\x01\\xff\\xff\\xff']" in RE_VAL:
                        print("Exiting")
                        OVEN.TTC_OFF()
                        RE_VAL.clear()
                        DIS.write("page Device Select\xff\xff\xff")
                        return

                    elif "['e\\x0f\\x1c\\x01\\xff\\xff\\xff']" in RE_VAL:
                        # DIS.write("rest\xff\xff\xff")
                        RE_VAL.clear()
                        DIS.write("page restart\xff\xff\xff")
                        os.system("sudo reboot")

                    print("07 - Updating Display...")

                    # creat file
                    sample_time = str(datetime.datetime.now()).replace(" ", "_").replace(".", "-").replace(":", "-")
                    name = 'Sample' + str(i)
                    locals()['v' + str(i)] = i
                    PA = CF.sample_folder(name)
                    CF.header_imp(PA, self.time_str, self.time_str, equipment_Info, test_mode,
                                      self.NEXTION_START_FREQ,
                                      self.NEXTION_END_FREQ, self.NEXTION_SET_VOLTAGE)

                    # run multimeter
                    print("04- Multimeter DMM196 Reading...")
                    if APP_IMP_PRESENT:
                        data = IMP.sweep_measure(self.NEXTION_START_FREQ, self.NEXTION_END_FREQ,
                                                        self.NEXTION_SET_VOLTAGE)
                        CF.content(PA, self.time_str, data)

                    # relay reset
                    print("06 - Swtich Relay Unselection: %d" % i)
                    REL.RelayDeSelect(i)

            else:
                if APP_NEXTION_PRESENT:
                    # run time
                    t_run = format(t_step - t_start, "0.2f")

                    Father.updateIMPSweep([temp_set, temp_real, TEMP_sensor, HUMI_sensor, t_run, "Waiting", " ", 0])

                    DE = str(DIS.read())
                    # print (DE)
                    RE_VAL.add(DE)
                    # print (RE_VAL)

                    if "['e\\x0f\\x1b\\x01\\xff\\xff\\xff']" in RE_VAL:
                        print("Exiting")
                        OVEN.TTC_OFF()
                        RE_VAL.clear()
                        DIS.write("page Device Select\xff\xff\xff")
                        return

                    elif "['e\\x0f\\x1c\\x01\\xff\\xff\\xff']" in RE_VAL:
                        # DIS.write("rest\xff\xff\xff")
                        RE_VAL.clear()
                        DIS.write("page restart\xff\xff\xff")
                        os.system("sudo reboot")

                    print("07 - Updating Display...")

                t1 = datetime.datetime.now()


if __name__ == "__main__":
    TTC = TTC_IMP_Manual()
    TTC.main(8, 25, 5, 13000, 1.1, None)

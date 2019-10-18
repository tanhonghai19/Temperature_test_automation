import sys
sys.path.append('/home/pi/Desktop/py/')
from time import sleep
import datetime
import VT4002_SM
import DMM_196
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
VT4002_IP = "169.254.80.96"
DMM_IP = "169.254.101.115"
DMM_PORT = 1234
NX_SERIAL_PORT = "/dev/ttyUSB0"  # COM7
I2C_address = 0x76

DIS = write_display.Nextion(NX_SERIAL_PORT)

command_sample = 'get n123.val\xff\xff\xff'

APP_OVEN_PRESENT = True
APP_DMM_196_PRESENT = True
APP_BME_280_PRESENT = True
APP_NEXTION_PRESENT = True
APP_PEN_DRIVE = True

# HUMIDITY SENSOR PARAMETERS
BME_280_INVALID_TEMP = -273
BME_280_INVALID_HUMI = -273

# RELAY PARAMETERS
RELAY_HOLDING_TIME = 1.94


class VT_DMM_Manual:
    def main(self, num_samples, set_temperature, Father):
        RE_VAL = set()

        # Initialize Relay
        REL = relay.Relay_module()
        REL.reset()

        # set PID parameters
        P = 15
        I = 0
        D = 0

        pid = PID.PID(P, I, D)
        pid.setSampleTime(1)

        if APP_NEXTION_PRESENT:
            self.NEXTION_NUM_SAMPLES = num_samples
            self.NEXTION_SET_TEMP = float(format(float(set_temperature) / 0.94, ".2f"))
        else:
            self.NEXTION_NUM_SAMPLES = 8
            self.NEXTION_SET_TEMP = 25

        # import oven and multimeter
        if APP_OVEN_PRESENT:
            OVEN = VT4002_SM.VT4002(VT4002_IP)
            OVEN.startComm()

        if APP_DMM_196_PRESENT:
            Multimeter = DMM_196.DMM_196(DMM_IP, DMM_PORT)
            Multimeter.startComm()

        # create file and title
        CF = data_storage.create_file()
        test_mode = "Manual"
        equipment_Info = "VT-4002 + DMM-196"
        Driver_root = detect_file.File(folder)[1]
        start_time = str(datetime.datetime.now())
        filename = start_time.replace(" ", "_").replace(".", "-").replace(":", "-")
        PATH = CF.folder(Driver_root, filename)
        CF.header(PATH, filename, start_time, equipment_Info, test_mode, self.NEXTION_NUM_SAMPLES)
        CF.content(PATH, filename,
                   ("Time(s)\tSetTemp.(oC)\tActual Temp.(oC)\tHumidity(%)\tTemp.Sensor(oC)\tSample number\tResistence(ohm)\r\n"))

        t_start = time.time()

        while True:
            # Relay reset
            REL.reset()

            for i in range(self.NEXTION_NUM_SAMPLES):
                if APP_OVEN_PRESENT:
                    # run oven)
                    print("01 - Reading data from Oven...")
                    temp = OVEN.read_temp()
                    temp_set = temp[0]
                    temp_real = temp[1]
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
                print("02 - Reading data from Humidity Sensor: Temp(oC): ", TEMP_sensor)
                print("02 - Reading data from Humidity Sensor: Humi(%): ", HUMI_sensor)

                print("Sensor Temperature : ", str(TEMP_sensor))

                pid.update(TEMP_sensor)

                target_temperature = pid.output

                if target_temperature > 130:
                    target_temperature = 130
                elif target_temperature < -40:
                    target_temperature = -40
                else:
                    target_temperature = target_temperature

                print("PID set Temperature : ", str(target_temperature))
                print("Chamber real Temperature : ", temp_real)

                OVEN.set_temp(target_temperature)

                # run time
                t_step = time.time()
                t_run = format(t_step - t_start, "0.2f")

                # relay selection
                print("03 - Swtich Relay: %d" % i)
                REL.RelaySelect(i)
                sleep(RELAY_HOLDING_TIME)

                # run multimeter
                print("04- Multimeter DMM196 Reading...")
                if APP_DMM_196_PRESENT:
                    mval = Multimeter.read_resiatance()
                else:
                    mval = (i * float(t_run))

                R_value = str(mval)

                # relay reset
                print("05 - Swtich Relay Unselection: %d" % i)
                REL.RelayDeSelect(i)

                # Persistency
                print("06 - Saving data...")
                result1 = []
                result2 = []
                result1.append([str(t_run), str(temp_set), str(temp_real), str(HUMI_sensor), str(TEMP_sensor), str(i), str(R_value)])
                CF.content(PATH, filename, result1)

                # create file for each sample
                result2.append([str(t_run), str(temp_set), str(temp_real), str(HUMI_sensor), str(TEMP_sensor), str(i), str(R_value)])
                CF.content(PATH, 'Sample' + str(i), result2)

                Father.updateMultimeter([temp_set, temp_real, TEMP_sensor, HUMI_sensor, t_run, R_value, i])

                DE = str(DIS.read())
                # print (DE)
                RE_VAL.add(DE)
                # print (RE_VAL)

                if "['e\\x0e\\x13\\x01\\xff\\xff\\xff']" in RE_VAL:
                    print("Exiting")
                    OVEN.close()
                    RE_VAL.clear()
                    DIS.write("page Device Select\xff\xff\xff")
                    return

                elif "['e\\x0e\\x14\\x01\\xff\\xff\\xff']" in RE_VAL:
                    # DIS.write("rest\xff\xff\xff")
                    RE_VAL.clear()
                    DIS.write("page restart\xff\xff\xff")
                    os.system("sudo reboot")

                print("07 - Updating Display...")


if __name__ == "__main__":
    VT = VT_DMM_Manual()
    VT.main(8, 25)

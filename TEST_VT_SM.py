import sys
import datetime
import os
import time
from time import sleep
sys.path.append('/home/pi/Desktop/py/')
import write_display
from TempProfile import readTempProfile
import VT4002_SM
import bme280
import relay
import detect_file
import Sourcemeter_sweep
import data_storage
import PID

folder = "/media/pi/"
VT4002_IP = "169.254.80.96"
IP_addr = "169.254.101.115"
PORT = 1234
I2C_address = 0x76
NX_SERIAL_PORT = "/dev/ttyUSB0"

APP_OVEN_PRESENT = False
APP_Sourcemeter_PRESENT = True
APP_PEN_DRIVE = False
APP_BME_280_PRESENT = False
APP_NEXTION_PRESENT = False

# HUMIDITY SENSOR PARAMETERS
BME_280_INVALID_TEMP = -273
BME_280_INVALID_HUMI = -273

# RELAY PARAMETERS
RELAY_HOLDING_TIME = 1.94

DIS = write_display.Nextion(NX_SERIAL_PORT)


class VT_SM_Auto:
    def Update(self, list):
        self.updateList = list

    def main(self,num_samples, start_voltage, end_voltage, step_voltage, Father):
        # Initialize Relay
        self.REL = relay.Relay_module()
        self.REL.reset()

        # detect file
        if APP_PEN_DRIVE:
            FILE_NAME = detect_file.File(folder)[0]
        else:
            FILE_NAME = "/home/pi/Desktop/Temperature_profile.txt"

        # Load Profile
        TP = readTempProfile(FILE_NAME)
        print(TP)
        
        #sleep(5)

        P = 5
        I = 0
        D = 0

        pid = PID.PID(P, I, D)
        pid.setSampleTime(1)

        # import oven and multimeter
        if APP_OVEN_PRESENT:
            OVEN = VT4002_SM.VT4002(VT4002_IP)
            OVEN.startComm()

        if APP_Sourcemeter_PRESENT:
            self.Sourcemeter = Sourcemeter_sweep.SourceMeter(IP_addr, PORT)
            self.Sourcemeter.startComm()

        self.NEXTION_NUM_SAMPLES = num_samples
        self.NEXTION_START_VOLTAGE = start_voltage
        self.NEXTION_END_VOLTAGE = end_voltage
        self.NEXTION_STEP_VOLTAGE = step_voltage

        # create file and title
        self.CF = data_storage.create_file()
        self.test_mode = "Auto"
        self.equipment_Info = "VT-4002 + Sourcemeter-2602"
       # Driver_root = detect_file.File(folder)[1]
        Driver_root = "/home/pi/Desktop/"
        start_time = str(datetime.datetime.now())
        self.folder_name = start_time.replace(" ", "_").replace(".", "-").replace(":", "-")
        self.CF.folder(Driver_root, self.folder_name)

        t_start = time.time()

        for step in TP:
            #create folder for each step
            self.CF.folder_SM(step)

            # setting the oven
            step_time = step[1] * 60  # step_time in seconds
            step_temp = float(format(float(step[0]) / 0.94, ".2f"))

            print(step)
            #sleep(5)

            t1 = datetime.datetime.now()
            t2 = datetime.datetime.now() + datetime.timedelta(seconds=step_time)
            t3 = datetime.datetime.now() + datetime.timedelta(seconds=10)

            counter = 0
            while (t1 < t2):
                # run oven
                print('01 - Reading data from Oven...')
                if APP_OVEN_PRESENT:
                    temp = OVEN.read_temp()
                    temp_set = temp[0]
                    temp_real = temp[1]
                else:
                    temp_set = format(1.00, "0.2f")
                    temp_real = format(1.00, "0.2f")

                # Humidity Sensor
                # If is not OK => apply non valid temp and humidity
                print('02 - Reading data from Humidity Sensor...')
                if APP_BME_280_PRESENT:
                    try:
                        temperature, pressure, humidity = bme280.readBME280All()

                        # Medicine
                        if ((humidity == None) or (temperature == None)):
                            humidity = BME_280_INVALID_HUMI
                            temperature = BME_280_INVALID_TEMP
                            print('02 - Reading data from Humidity Sensor (NONE! - ERROR)...')
                        elif ((type(humidity) == str) or (type(temperature) == str)):
                            humidity = BME_280_INVALID_HUMI
                            temperature = BME_280_INVALID_TEMP
                            print('02 - Reading data from Humidity Sensor (INVALID STRING! - ERROR)...')

                    except:
                        humidity = BME_280_INVALID_HUMI
                        temperature = BME_280_INVALID_TEMP
                        print('02 - Reading data from Humidity Sensor (INVALID STRING! - ERROR)...')

                else:
                    print('02 - Reading data from Humidity Sensor (DISABLED)...')
                    humidity = BME_280_INVALID_HUMI
                    temperature = BME_280_INVALID_TEMP

                HUMI_sensor = format(humidity, "0.2f")
                TEMP_sensor = format(temperature, "0.2f")
                print('02 - Reading data from Humidity Sensor: Temp(oC): ', TEMP_sensor)
                print('02 - Reading data from Humidity Sensor: Humi(%): ', HUMI_sensor)

                # run oven
                if APP_OVEN_PRESENT:
                    pid.SetPoint = step_temp
                    pid.setKp(float(P))
                    pid.setKi(float(I))
                    pid.setKd(float(D))

                    temp = OVEN.read_temp()
                    temp_real = str(temp[1])

                    self.actual_temperature = temperature

                    print("Sensor Temperature : " + str(self.actual_temperature))

                    pid.update(self.actual_temperature)

                    target_temperature = pid.output

                    if target_temperature > 130:
                        target_temperature = 130
                    elif target_temperature < -40:
                        target_temperature = -40
                    else:
                        target_temperature = target_temperature

                    print("PID set Temperature : " + str(target_temperature))
                    print("Chamber real Temperature : " + temp_real)

                    OVEN.set_temp(target_temperature)

                if t1 > t3 and t1 < t2 and counter < 2:
                    for i in range(self.NEXTION_NUM_SAMPLES):
                        print('03 - Swtich Relay: %d' % i)
                        self.REL.RelaySelect(i)
                        sleep(RELAY_HOLDING_TIME)

                        # create folder for each sample
                        current_time = str(datetime.datetime.now())
                        self.time_str = current_time.replace(" ", "_").replace(".", "-").replace(":", "-")

                        name = 'Sample' + str(i)
                        locals()['v' + str(i)] = i
                        PA = self.CF.sample_folder(name)
                        self.CF.header_sm(PA, self.time_str, self.time_str, self.equipment_Info, self.test_mode, self.NEXTION_NUM_SAMPLES, self.NEXTION_START_VOLTAGE,
                                    self.NEXTION_END_VOLTAGE, self.NEXTION_STEP_VOLTAGE, 10)

                        print('04 - Sourcemeter Reading...')
                        # measurement of sourcemeter
                        if APP_Sourcemeter_PRESENT:
                            data = self.Sourcemeter.Measure('a', self.NEXTION_START_VOLTAGE, self.NEXTION_END_VOLTAGE,
                                                       self.NEXTION_STEP_VOLTAGE, self)
                            self.CF.content(PA, self.time_str, data)

                        print('05 - Swtich Relay Unselection: %d' % i)
                        self.REL.RelayDeSelect(i)

                        if APP_NEXTION_PRESENT:
                            print('07 - Reading Display...')
                            RE_VAL = set()
                            DE = str(DIS.read())
                            # print (DE)
                            RE_VAL.add(DE)
                            # print (RE_VAL)

                            if "['e\\x05\\x15\\x01\\xff\\xff\\xff']" in RE_VAL:
                                DIS.write('t0.txt="Stop"')
                                OVEN.close()
                                sys.exit()

                            elif "['e\\x05\\x14\\x01\\xff\\xff\\xff']" in RE_VAL:
                                # DIS.write("rest\xff\xff\xff")
                                os.system("sudo reboot")

                            print('07 - Updating Display...')

                            Father.Update(self.updateList)

                counter += 1

                t1 = datetime.datetime.now()

        if APP_OVEN_PRESENT:
            OVEN.close()


if __name__ == "__main__":
    VS = VT_SM_Auto()
    VS.main(2, -40, 40, 1)

import sys
sys.path.append('/home/pi/Desktop/py/')
from time import sleep
import time
import  os
import datetime
import csv
import TTC4006_Tira
from TempProfile import readTempProfile
import bme280
import Keithley_2602_Eth
import relay
import PID
import detect_file
import data_storage
import write_display


folder = "/media/pi/"

TTC_SERIAL_PORT = '/dev/ttyUSB1'
TTC_SERIAL_BAUD = 19200
TTC_ADDRESS = 17
I2C_address = 0x76
SM_IP = "169.254.80.115"
SM_PORT = 1234
NX_SERIAL_PORT = "/dev/ttyUSB0"  # COM7

DIS = write_display.Nextion(NX_SERIAL_PORT)

# HUMIDITY SENSOR PARAMETERS
BME_280_INVALID_TEMP = -273
BME_280_INVALID_HUMI = -273

# RELAY PARAMETERS
RELAY_HOLDING_TIME = 1.94

APP_OVEN_PRESENT = True
APP_Sourcemeter_PRESENT = True
APP_BME_280_PRESENT = True
APP_NEXTION_PRESENT = True
APP_PEN_DRIVE = True


class TTC_SM_Auto:
    def main(self,num_samples, set_temperature, Father):
        # Initialize Relay
        REL = relay.Relay_module()
        REL.reset()

        # detect file
        if APP_PEN_DRIVE:
            FILE_NAME = detect_file.File(folder)[0]
        else:
            FILE_NAME = "/home/pi/Desktop/Temperature_profile.txt"

        # Load Profile
        VOL = readTempProfile(FILE_NAME)[0]
        print(VOL)

        self.NEXTION_NUM_SAMPLES = num_samples
        self.NEXTION_SET_temperature = set_temperature

        # import oven and multimeter
        if APP_OVEN_PRESENT:
            OVEN = TTC4006_Tira.TTC4006( TTC_SERIAL_PORT )
            OVEN.TTC_ON()
            OVEN.TTC_ENABLE_TEMP()

        P = 5
        I = 0
        D = 0

        pid = PID.PID(P, I, D)
        pid.setSampleTime(1)

        if APP_Sourcemeter_PRESENT:
            Sourcemeter = Keithley_2602_Eth.SourceMeter(SM_IP, SM_PORT)
            Sourcemeter.startComm()

        # create file and title
        CF = data_storage.create_file()
        test_mode = "Auto"
        equipment_Info = "TTC-4006 + Sourcemeter-2602"
        Driver_root = detect_file.File(folder)[1]
        start_time = str(datetime.datetime.now())
        filename = start_time.replace(" ", "_").replace(".", "-").replace(":", "-")
        PATH = CF.folder(Driver_root, filename)
        CF.header(PATH, filename, start_time, equipment_Info, test_mode, self.NEXTION_NUM_SAMPLES)
        CF.content(PATH, filename,
                   ("Time(s)\tSetTemp.(oC)\tActual Temp.(oC)\tHumidity(%)\tTemp.Sensor(oC)\tSample number\tCurrent(A)\tResistence(ohm)\r\n"))

        t_start = time.time()

        for step in VOL:
            print(step)
            # setting the oven
            step_time = step[0] * 60  # step_time in seconds
            step_temp = float(format(float(self.NEXTION_SET_temperature) / 0.84, ".2f"))


            t1 = datetime.datetime.now( )
            t2 = datetime.datetime.now() + datetime.timedelta(seconds=step_time)

            while( t1 < t2 ):
                # Relay switching
                REL.reset()

                for i in range(self.NEXTION_NUM_SAMPLES):
                    if APP_OVEN_PRESENT:
                        # run oven)
                        print('01 - Reading data from Oven...')
                        temp_real = OVEN.TTC_Read_PV_Temp()
                        temp_set = OVEN.TTC_Read_SP_Temp()
                    else:
                        temp_set = format(1.00, "0.2f")
                        temp_real = format(1.00, "0.2f")

                    pid.SetPoint = self.NEXTION_SET_temperature
                    pid.setKp(float(P))
                    pid.setKi(float(I))
                    pid.setKd(float(D))

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

                    print("Sensor Temperature : ", str(TEMP_sensor))

                    pid.update(float(TEMP_sensor))

                    target_temperature = pid.output

                    if target_temperature > 180:
                        target_temperature = 180
                    elif target_temperature < -40:
                        target_temperature = -40
                    else:
                        target_temperature = target_temperature

                    OVEN.TTC_Set_Temp(target_temperature)

                    print("PID set Temperature : ", str(target_temperature))
                    print("Chamber real Temperature : ", temp_real)

                    # run time
                    t_step = time.time()
                    t_run = format(t_step - t_start, "0.2f")

                    REL.RelaySelect(i)
                    sleep(RELAY_HOLDING_TIME)

                    if APP_Sourcemeter_PRESENT:
                        fcurrent = Sourcemeter.Measure('a', self.NEXTION_SET_VOLTAGE)
                        print("Reading Sourcemeter:", i)
                    else:
                        fcurrent = (i*float(t_run))

                    I_Value = format(float(fcurrent), '.3E')

                    R_Value = format(self.NEXTION_SET_VOLTAGE / float(I_Value),'.3E')

                    print("Resistance:", R_Value)
                    print("")

                    REL.RelayDeSelect(i)

                    # Persistency
                    print('06 - Saving data...')
                    CF.content(PATH, filename, (
                        str(t_run), str(temp_set), str(temp_real), str(HUMI_sensor), str(TEMP_sensor), str(i),
                        str(I_Value),
                        str(R_Value)))

                    # create file for each sample
                    CF.content(PATH, 'Sample' + str(i), (
                        str(t_run), str(temp_set), str(temp_real), str(HUMI_sensor), str(TEMP_sensor), str(i),
                        str(I_Value),
                        str(R_Value)))

                    if APP_NEXTION_PRESENT:
                        print('07 - Reading Display...')
                        RE_VAL = set()
                        DE = str(DIS.read())
                        # print (DE)
                        RE_VAL.add(DE)
                        # print (RE_VAL)

                        if "['e\\x05\\x15\\x01\\xff\\xff\\xff']" in RE_VAL:
                            DIS.write('t0.txt="Stop"')
                            OVEN.TTC_OFF()
                            sys.exit()

                        elif "['e\\x05\\x14\\x01\\xff\\xff\\xff']" in RE_VAL:
                            # DIS.write("rest\xff\xff\xff")
                            os.system("sudo reboot")
                            break

                        print('07 - Updating Display...')

                        if Father != None:
                            Father.updateMultimeter([temp_set, temp_real, TEMP_sensor, HUMI_sensor, t_run, R_Value, i])

                t1 = datetime.datetime.now()

        if APP_OVEN_PRESENT:
            OVEN.TTC_OFF()


if __name__ == "__main__":
    TTC = TTC_SM_Auto()
    TTC.main(1, 2, None)



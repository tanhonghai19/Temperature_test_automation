import sys
sys.path.append('/home/pi/Desktop/py/')
from time import sleep
import datetime
import TTC4006_Tira
from TempProfile import readTempProfile
import DMM_196
import bme280
import relay
import detect_file
import write_display
import time
import data_storage
import os
import PID

#FILE_NAME = "/media/pi/B49E-19751/Temperature_profile.txt"
folder = "/media/pi/"

TTC_SERIAL_PORT = '/dev/ttyUSB1'
TTC_SERIAL_BAUD = 19200
TTC_ADDRESS = 17
DMM_IP = "169.254.80.115"
DMM_PORT = 1234
NX_SERIAL_PORT = "/dev/ttyUSB0"  # COM7
I2C_address = 0x76

DIS = write_display.Nextion(NX_SERIAL_PORT)

# HUMIDITY SENSOR PARAMETERS
BME_280_INVALID_TEMP = -273
BME_280_INVALID_HUMI = -273

# RELAY PARAMETERS
RELAY_HOLDING_TIME = 1.94

APP_OVEN_PRESENT = True
APP_DMM_196_PRESENT = True
APP_BME_280_PRESENT = True
APP_NEXTION_PRESENT = True
APP_PEN_DRIVE = True


class TTC_DMM_Auto:
    def main(self, num_samples, Father):
        RE_VAL = set()

        # Initialize Relay
        REL = relay.Relay_module()
        REL.reset()

        # detect file
        if APP_PEN_DRIVE:
            FILE_NAME = detect_file.File(folder)[0]

        # Load Profile
        TP = readTempProfile(FILE_NAME)[0]
        print(TP)

        # set PID parameters
        P = 5
        I = 0
        D = 0

        pid = PID.PID(P, I, D)
        pid.setSampleTime(1)

        # get sample number
        if APP_NEXTION_PRESENT:
            self.NEXTION_NUM_SAMPLES = num_samples
        else:
            self.NEXTION_NUM_SAMPLES = 8

        # import oven and multimeter
        if APP_OVEN_PRESENT:
            OVEN = TTC4006_Tira.TTC4006( TTC_SERIAL_PORT )
            OVEN.TTC_ON()
            OVEN.TTC_ENABLE_TEMP()

        if APP_DMM_196_PRESENT:
            Multimeter = DMM_196.DMM_196(DMM_IP, DMM_PORT)
            Multimeter.startComm()

        # create file and title
        CF = data_storage.create_file()
        test_mode = "Auto"
        equipment_Info = "TTC-4006 + DMM-196"
        Driver_root = detect_file.File(folder)[1]
        start_time = str(datetime.datetime.now())
        filename = start_time.replace(" ", "_").replace(".", "-").replace(":", "-")
        PATH = CF.folder(Driver_root, filename)
        CF.header(PATH, filename, start_time, equipment_Info, test_mode, self.NEXTION_NUM_SAMPLES)
        CF.content(PATH, filename, ("Time(s)\tSetTemp.(oC)\tActual Temp.(oC)\tHumidity(%)\tTemp.Sensor(oC)\tSample number\tResistence(ohm)\r\n"))

        t_start = time.time()

        # temperature loop
        for step in TP:
            # setting the oven
            step_time = step[0] * 60  # step_time in seconds
            step_temp = float(format(float(step[1]) / 0.84, ".2f"))

            print( step )

            t1 = datetime.datetime.now( )
            t2 = datetime.datetime.now() + datetime.timedelta(seconds=step_time)

            while( t1 < t2 ):
                # Relay switching
                REL.reset()

                for i in range(self.NEXTION_NUM_SAMPLES):
                    # run oven
                    if APP_OVEN_PRESENT:
                        temp_set1 = OVEN.TTC_Read_SP_Temp()
                        temp_real1 = OVEN.TTC_Read_PV_Temp()
                        temp_set = str(format(temp_set1, "0,.2f"))
                        temp_real = str(format(temp_real1, "0,.2f"))

                    else:
                        temp_set = format(1.00, "0.2f")
                        temp_real = format(1.00, "0.2f")

                    pid.SetPoint = step_temp
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

                    if APP_OVEN_PRESENT:
                        OVEN.TTC_Set_Temp(target_temperature)

                    # run time
                    t_step = time.time()
                    t_r = t_step - t_start
                    t_run = format(t_r, "0.2f")

                    REL.RelaySelect(i)
                    sleep(RELAY_HOLDING_TIME)

                    # run multimeter
                    print('04- Multimeter DMM196 Reading...')
                    if APP_DMM_196_PRESENT:
                        mval = Multimeter.read_resiatance()
                    else:
                        mval = (i * float(t_run))

                    R_value = str(mval)

                    # relay reset
                    REL.RelayDeSelect(i)


                    # Persistency
                    print('06 - Saving data...')
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
                        OVEN.TTC_OFF()
                        RE_VAL.clear()
                        DIS.write("page Device Select\xff\xff\xff")
                        return

                    elif "['e\\x0e\\x14\\x01\\xff\\xff\\xff']" in RE_VAL:
                        # DIS.write("rest\xff\xff\xff")
                        RE_VAL.clear()
                        DIS.write("page restart\xff\xff\xff")
                        os.system("sudo reboot")

                    print("07 - Updating Display...")

                t1 = datetime.datetime.now()

        if APP_OVEN_PRESENT:
            OVEN.TTC_OFF()


if __name__ == "__main__":
    TTC = TTC_DMM_Auto()
    TTC.main(8, None)
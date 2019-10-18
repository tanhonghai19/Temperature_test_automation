import sys
sys.path.append('/home/pi/Desktop/py/')
from time import sleep
import datetime
import TTC4006_Tira
from TempProfile import readTempProfile
import LCR_Eth
import bme280
import relay
import detect_file
import write_display
import PID
import data_storage
import time
import  os

#FILE_NAME = "/media/pi/B49E-19751/Temperature_profile.txt"
folder = "/media/pi/"

TTC_SERIAL_PORT = "/dev/ttyUSB1"
TTC_SERIAL_BAUD = 19200
TTC_ADDRESS = 17
#MX_SERIAL_PORT = "COM5"

LCR__IP = "169.254.101.115"# COM3
LCR_Port = 1234
NX_SERIAL_PORT = "/dev/ttyUSB0"  # COM7
I2C_address = 0x76

DIS = write_display.Nextion(NX_SERIAL_PORT)

# HUMIDITY SENSOR PARAMETERS
BME_280_INVALID_TEMP = -273
BME_280_INVALID_HUMI = -273

APP_OVEN_PRESENT = True
APP_LCR_PRESENT = True
APP_BME_280_PRESENT = True
APP_NEXTION_PRESENT = False
APP_PEN_DRIVE = False

class TTC_LCR_Auto:
    def main(self, num_samples, voltage, frequency, Father):
        RE_VAL = set()

        # Initialize Relay
        REL = relay.Relay_module()
        REL.reset()

        # detect file
        if APP_PEN_DRIVE:
            FILE_NAME = detect_file.File(folder)[0]
        else:
            FILE_NAME = "/home/pi/Desktop/Temperature_profile.txt"

        # Load Profile
        TP = readTempProfile(FILE_NAME)[0]
        print(TP)

        self.NEXTION_NUM_SAMPLES = num_samples

        if APP_OVEN_PRESENT:
            OVEN = TTC4006_Tira.TTC4006( TTC_SERIAL_PORT )
            OVEN.TTC_ON()
            OVEN.TTC_ENABLE_TEMP()

        P = 5
        I = 0
        D = 0

        pid = PID.PID(P, I, D)
        pid.setSampleTime(1)

        if APP_LCR_PRESENT:
            LCR = LCR_Eth.LCR_Meter(LCR__IP, LCR_Port)
            LCR.startComm()

        # create file and title
        CF = data_storage.create_file()
        test_mode = "Auto"
        equipment_Info = "TTC-4006 + LCR-4284A"

        if APP_PEN_DRIVE:
            Driver_root = detect_file.File(folder)[1]
        else:
            Driver_root = "/home/pi/Desktop/TTC_LCR/"

        start_time = str(datetime.datetime.now())
        filename = start_time.replace(" ", "_").replace(".", "-").replace(":", "-")
        PATH = CF.folder(Driver_root, filename)
        CF.header(PATH, filename, start_time, equipment_Info, test_mode, self.NEXTION_NUM_SAMPLES)
        CF.content(PATH, filename,
                   "Time(s)\tSetTemp.(oC)\tActual Temp.(oC)\tHumidity(%)\tTemp.Sensor(oC)\tSample number\tR\tX\tCP\tRP\r\n")

        t_start = time.time()

        for step in TP:
            print(step)
            # setting the oven
            step_time = step[0] * 60  # step_time in seconds
            step_temp = float(format(float(step[1]) / 0.84, ".2f"))

            t1 = datetime.datetime.now()
            t2 = datetime.datetime.now() + datetime.timedelta(seconds=step_time)

            while (t1 < t2):
                # Relay switching
                REL.reset()

                for i in range(self.NEXTION_NUM_SAMPLES):
                    if APP_OVEN_PRESENT:
                        # run oven)
                        print("01 - Reading data from Oven...")
                        temp_real = OVEN.TTC_Read_PV_Temp()
                        temp_set = OVEN.TTC_Read_SP_Temp()
                    else:
                        temp_set = format(1.00, "0.2f")
                        temp_real = format(1.00, "0.2f")

                    pid.SetPoint = step_temp
                    pid.setKp(float(P))
                    pid.setKi(float(I))
                    pid.setKd(float(D))

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
                    print("2 - Reading data from Humidity Sensor: Temp(oC): ", TEMP_sensor)
                    print("02 - Reading data from Humidity Sensor: Humi(%): ", HUMI_sensor)

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
                    t_r = t_step - t_start
                    t_run = format(t_r, "0.2f")

                    REL.RelaySelect(i)

                    if APP_LCR_PRESENT:
                        FinalD = LCR.measure(voltage, frequency)
                        print("LCR Reading: ", FinalD)
                        CP = str(FinalD[0])
                        RP = str(FinalD[1])
                        R_value = str(FinalD[2])
                        X_value = str(FinalD[3])
                    else:
                        CP = 0
                        RP = 0
                        R_value = 0
                        X_value = 0

                    REL.RelayDeSelect(i)

                    # Persistency
                    print('06 - Saving data...')
                    print("")
                    result1 = []
                    result2 = []
                    result1.append([
                    str(t_run), str(step[1]), str(temp_real), str(HUMI_sensor), str(TEMP_sensor), str(i),
                    str(R_value), str(X_value), str(CP), str(RP)])
                    CF.content(PATH, filename, result1)

                    # create file for each sample
                    result2.append([str(t_run), str(step[1]), str(temp_real), str(HUMI_sensor), str(TEMP_sensor), str(i),
                    str(R_value), str(X_value), str(CP), str(RP)])
                    CF.content(PATH, 'Sample' + str(i), result2)

                    Father.Update([temp_set, temp_real, TEMP_sensor, humidity, t_run, R_value, X_value, i])

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

        if APP_OVEN_PRESENT:
            OVEN.TTC_OFF()


if __name__ == "__main__":
    TTC = TTC_LCR_Auto()
    TTC.main(8, 5, 1, None)
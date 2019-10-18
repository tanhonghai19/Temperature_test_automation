import sys
sys.path.append('/home/pi/Desktop/py/')
from time import sleep
import time
import  os
import datetime
import csv
import VT4002_SM
from TempProfile import readTempProfile
import bme280
import Keithley_2602_Eth
import relay
import PID
import data_storage
import detect_file
import write_display


folder = "/media/pi/"
VT4002_IP = "169.254.101.96"
I2C_address = 0x76
SM_IP = "169.254.101.115"
SM_PORT = 1234
NX_SERIAL_PORT = "/dev/ttyUSB0"  # COM7

DIS = write_display.Nextion(NX_SERIAL_PORT)

equipment_Info ="Keithley Instruments Inc., Model 2602, 1073756, 1.3.4"

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


class VT_SM_Auto:
    def main(self,num_samples, set_voltage, Father):
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
        self.NEXTION_SET_VOLTAGE = set_voltage

        # import oven and multimeter
        if APP_OVEN_PRESENT:
            OVEN = VT4002_SM.VT4002(VT4002_IP)
            OVEN.startComm()

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
        equipment_Info = "VT-4002 + Sourcemeter 2602"
        Driver_root = detect_file.File(folder)[1]
        start_time = str(datetime.datetime.now())
        filename = start_time.replace(" ", "_").replace(".", "-").replace(":", "-")
        PATH = CF.folder(Driver_root, filename)
        CF.header(PATH, filename, start_time, equipment_Info, test_mode, self.NEXTION_NUM_SAMPLES)
        CF.content(PATH, filename,
                   ("Time(s)\tSetTemp.(oC)\tActual Temp.(oC)\tHumidity(%)\tTemp.Sensor(oC)\tSample number\tCurrent(A)\tResistence(ohm)\r\n"))

        t_start = time.time()

        for step in TP:
            print(step)
            # setting the oven
            step_time = step[0] * 60  # step_time in seconds
            step_temp = float(format(float(step[1]) / 0.94, ".2f"))

            t1 = datetime.datetime.now()
            t2 = datetime.datetime.now() + datetime.timedelta(seconds=step_time)

            while( t1 < t2 ):
                # Relay switching
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
                    print("02 - Reading data from Humidity Sensor: Temp(oC): ", TEMP_sensor)
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

                    OVEN.set_temp(target_temperature)

                    print("PID set Temperature : ", str(target_temperature))
                    print("Chamber real Temperature : ", temp_real)

                    # run time
                    t_step = time.time()
                    t_run = format(t_step - t_start, "0.2f")

                    REL.RelaySelect(i)
                    sleep(RELAY_HOLDING_TIME)

                    if APP_Sourcemeter_PRESENT:
                        fcurrent = Sourcemeter.Measure("a", self.NEXTION_SET_VOLTAGE)
                        print("Reading Sourcemeter:", i)
                    else:
                        fcurrent = (i*float(t_run))

                    I_Value = format(fcurrent, ".3E")

                    R_Value = format(self.NEXTION_SET_VOLTAGE / float(I_Value), ".3E")

                    print("Resistance:", R_Value)
                    print("")

                    REL.RelayDeSelect(i)

                    # Persistency
                    print("06 - Saving data...")
                    result1 = []
                    result2 = []
                    result1.append([
                        str(t_run), str(step[1]), str(temp_real), str(HUMI_sensor), str(TEMP_sensor), str(i),
                        str(I_Value),
                        str(R_Value)])
                    CF.content(PATH, filename, result1)

                    # create file for each sample
                    result2.append([
                        str(t_run), str(step[1]), str(temp_real), str(HUMI_sensor), str(TEMP_sensor), str(i),
                        str(I_Value),
                        str(R_Value)])
                    CF.content(PATH, "Sample" + str(i), result2)

                    Father.updateMultimeter([temp_set, temp_real, TEMP_sensor, HUMI_sensor, t_run, R_Value, i])

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

                t1 = datetime.datetime.now()

        if APP_OVEN_PRESENT:
            OVEN.close()


if __name__ == "__main__":
    VT = VT_SM_Auto()
    VT.main(8, 5)



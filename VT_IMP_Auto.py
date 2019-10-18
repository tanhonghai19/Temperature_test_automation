import sys

sys.path.append('/home/pi/Desktop/py/')
from time import sleep
import datetime
import VT4002_SM
import Impedanz_4192A_Eth
from TempProfile import readTempProfile
import bme280
import time
import detect_file
import relay
import write_display
import os
import data_storage
import PID

import threading
from threading import Thread

# FILE_NAME = "/media/pi/B49E-19751/Temperature_profile.txt"
folder = "/media/pi/"
VT4002_IP = "169.254.101.96"
IMP_IP = "169.254.80.115"
IMP_PORT = 1234
NX_SERIAL_PORT = "/dev/ttyUSB0"  # COM7
I2C_address = 0x76

DIS = write_display.Nextion(NX_SERIAL_PORT)

command_sample = "get n123.val\xff\xff\xff"

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


class OvenThread(Thread):
    def __init__(self, TP, Father, RE_VAL):
        Thread.__init__(self)
        # import oven and multimeter
        if APP_OVEN_PRESENT:
            self.OVEN = VT4002_SM.VT4002(VT4002_IP)
            self.OVEN.startComm()

        self.TP = TP
        self.RE_VAL = RE_VAL

        # set PID parameters
        self.P = 5
        self.I = 0
        self.D = 0

        self.pid = PID.PID(self.P, self.I, self.D)
        self.pid.setSampleTime(1)

        self.lock = threading.Lock()

        self.Father = Father

        self.t1 = 0
        self.t2 = 0
        self.t3 = 0

    def getTimes(self):
        return [self.t1,self.t2,self.t3]

    def getStepNum(self):
        return self.step_counter

    def getStep(self):
        return self.step

    def run(self):
        self.step_counter = 0
        for step in self.TP:
            self.lock.acquire()
            self.step = step
            self.lock.release()

            # setting the oven
            t_start = time.time()
            step_time = self.step[0] * 60  # step_time in seconds
            step_temp = float(format(float(self.step[1]) / 0.84, ".2f"))
            print(self.step)

            self.lock.acquire()
            self.t1 = datetime.datetime.now()
            self.t2 = datetime.datetime.now() + datetime.timedelta(seconds=step_time)
            self.t3 = datetime.datetime.now() + datetime.timedelta(seconds=1 * 60)
            self.lock.release()

            while self.t1 < self.t2:
                # run time
                t_step = time.time()
                t_run = format(t_step - t_start, "0.2f")

                if APP_OVEN_PRESENT:
                    # run oven)
                    print("01 - Reading data from Oven...")
                    temp = self.OVEN.read_temp()
                    temp_set = temp[0]
                    temp_real = temp[1]
                else:
                    temp_set = format(1.00, "0.2f")
                    temp_real = format(1.00, "0.2f")

                self.pid.SetPoint = step_temp
                self.pid.setKp(float(self.P))
                self.pid.setKi(float(self.I))
                self.pid.setKd(float(self.D))

                # read temperature sensor
                # Humidity Sensor
                # If is not OK => apply non valid temp and humidity
                print("02 - Reading data from Humidity Sensor...")
                if APP_BME_280_PRESENT:
                    try:
                        temperature, pressure, humidity = bme280.readBME280All()

                        # Medicine
                        if (humidity == None) or (temperature == None):
                            humidity = BME_280_INVALID_HUMI
                            temperature = BME_280_INVALID_TEMP
                            print("02 - Reading data from Humidity Sensor (NONE! - ERROR)...")
                        elif (type(humidity) == str) or (type(temperature) == str):
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

                self.pid.update(float(TEMP_sensor))

                target_temperature = self.pid.output

                # Limit Extremes
                if target_temperature > 130:
                    target_temperature = 130
                elif target_temperature < -40:
                    target_temperature = -40
                else:
                    target_temperature = target_temperature

                print("PID set Temperature : ", str(target_temperature))
                print("Chamber real Temperature : ", temp_real)

                self.OVEN.set_temp(target_temperature)

                if APP_NEXTION_PRESENT:
                    self.Father.updateIMPTemp([temp_set, temp_real, TEMP_sensor, HUMI_sensor, t_run])

                self.lock.acquire()
                self.t1 = datetime.datetime.now()
                self.lock.release()

                DE = str(DIS.read())
                # print (DE)
                self.RE_VAL.add(DE)
                # print (RE_VAL)

                if "['e\\x0f\\x1b\\x01\\xff\\xff\\xff']" in self.RE_VAL:
                    print("Exiting")
                    self.OVEN.close()
                    self.RE_VAL.clear()
                    DIS.write("page Device Select\xff\xff\xff")
                    return

                elif "['e\\x0f\\x1c\\x01\\xff\\xff\\xff']" in self.RE_VAL:
                    # DIS.write("rest\xff\xff\xff")
                    self.RE_VAL.clear()
                    DIS.write("page restart\xff\xff\xff")
                    os.system("sudo reboot")

                print("07 - Updating Display...")

                sleep(0.5)

            self.lock.acquire()
            self.step_counter += 1
            self.lock.release()

        self.OVEN.close()

class MeasureThread(Thread):
    def __init__(self, num_samples, start_freq, end_freq, set_voltage, Father, RE_VAL):
        Thread.__init__(self)
        # Initialize Relay
        self.REL = relay.Relay_module()
        self.REL.reset()

        if APP_IMP_PRESENT:
            self.IMP = Impedanz_4192A_Eth.Impedance_Analyser(IMP_IP, IMP_PORT)
            self.IMP.startComm()

        # create file and title
        self.CF = data_storage.create_file()
        self.test_mode = "Auto"
        self.equipment_Info = "TTC-4006 + IMP-4192A"
        Driver_root = detect_file.File(folder)[1]
        start_time = str(datetime.datetime.now())
        filename = start_time.replace(" ", "_").replace(".", "-").replace(":", "-")
        self.CF.folder(Driver_root, filename)

        self.Oven = getCurrentOven( )

        self.CurrentStep = -1

        self.NEXTION_NUM_SAMPLES = num_samples
        self.NEXTION_START_FREQ = start_freq
        self.NEXTION_END_FREQ = end_freq
        self.NEXTION_SET_VOLTAGE = set_voltage

        self.Father = Father
        self.RE_VAL = RE_VAL

    def run(self):
        while(1):
            T = self.Oven.getTimes()
            S = self.Oven.getStepNum()
            StepContent = self.Oven.getStep()
            if T[0] > T[2] and T[0] < T[1] and S != self.CurrentStep:
                self.CurrentStep = S
                # create folder for each step
                self.CF.folder_IMP( StepContent )
                for i in range(self.NEXTION_NUM_SAMPLES):
                    # relay selection
                    print("03 - Swtich Relay: %d" % i)
                    self.REL.RelaySelect(i)
                    sleep(RELAY_HOLDING_TIME)

                    # create folder for each sample
                    current_time = str(datetime.datetime.now())
                    self.time_str = current_time.replace(" ", "_").replace(".", "-").replace(":", "-")

                    self.Father.updateIMPSweep(["Measuring", " ", i])

                    DE = str(DIS.read())
                    # print (DE)
                    self.RE_VAL.add(DE)
                    # print (RE_VAL)

                    if "['e\\x0f\\x1b\\x01\\xff\\xff\\xff']" in self.RE_VAL:
                        print("Exiting")
                        self.Oven.OVEN.close()
                        self.RE_VAL.clear()
                        DIS.write("page Device Select\xff\xff\xff")
                        return

                    elif "['e\\x0f\\x1c\\x01\\xff\\xff\\xff']" in self.RE_VAL:
                        # DIS.write("rest\xff\xff\xff")
                        self.RE_VAL.clear()
                        DIS.write("page restart\xff\xff\xff")
                        os.system("sudo reboot")

                    print("07 - Updating Display...")

                    # creat file
                    sample_time = str(datetime.datetime.now()).replace(" ", "_").replace(".", "-").replace(":", "-")
                    name = "Sample" + str(i)
                    locals()['v' + str(i)] = i
                    PA = self.CF.step_folder(name)
                    self.CF.header_imp(PA, self.time_str, self.time_str, self.equipment_Info, self.test_mode,
                                  self.NEXTION_START_FREQ,
                                  self.NEXTION_END_FREQ, self.NEXTION_SET_VOLTAGE)

                    # run multimeter
                    print("04- Multimeter DMM196 Reading...")
                    if APP_IMP_PRESENT:
                        data = self.IMP.sweep_measure(self.NEXTION_START_FREQ, self.NEXTION_END_FREQ,
                                                 self.NEXTION_SET_VOLTAGE)
                        self.CF.content(PA, self.time_str, data)

                    # relay reset
                    print("06 - Swtich Relay Unselection: %d" % i)
                    self.REL.RelayDeSelect(i)
                break
            else:
                self.Father.updateIMPStatus(["Waiting", " ", 0])

                DE = str(DIS.read())
                # print (DE)
                self.RE_VAL.add(DE)
                # print (RE_VAL)

                if "['e\\x0f\\x1b\\x01\\xff\\xff\\xff']" in self.RE_VAL:
                    print("Exiting")
                    self.Oven.OVEN.close()
                    self.RE_VAL.clear()
                    DIS.write("page Device Select\xff\xff\xff")
                    return

                elif "['e\\x0f\\x1c\\x01\\xff\\xff\\xff']" in self.RE_VAL:
                    # DIS.write("rest\xff\xff\xff")
                    self.RE_VAL.clear()
                    DIS.write("page restart\xff\xff\xff")
                    os.system("sudo reboot")

                print("07 - Updating Display...")
                print("Waiting...")
                print(T)
                print(S)
                print(StepContent)
            sleep(1)

def getCurrentOven( ):
    global curOven
    return curOven


class VT_IMP_Auto:
    def main(self, num_samples, start_freq, end_freq, set_voltage, Father):
        global curOven

        # Initialize screen
        self.RE_VAL = set()
        DE = str(DIS.read())
        # print (DE)
        self.RE_VAL.add(DE)
        # print (RE_VAL)

        # detect file
        if APP_PEN_DRIVE:
            FILE_NAME = detect_file.File(folder)[0]
        else:
            FILE_NAME = "/home/pi/Desktop/Temperature_profile.txt"

        # Load Profile
        TP = readTempProfile(FILE_NAME)[0]
        print(TP)

        o = OvenThread(TP, Father,self.RE_VAL)
        curOven = o
        m = MeasureThread(num_samples, start_freq, end_freq, set_voltage, Father, self.RE_VAL)

        o.start( )
        m.start( )



if __name__ == "__main__":
    VT = VT_IMP_Auto()
    VT.main(8, 5, 13000, 1.1, None)

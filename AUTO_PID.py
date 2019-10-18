import sys

sys.path.append('/home/pi/Desktop/py/')
import TTC4006_Tira
import PID
import bme280
from TempProfile import readTempProfile
import datetime
import time
# from PrintLOG_2 import PrintLOG
import time as te
folder = "/media/pi/"
TTC_SERIAL_PORT = '/dev/ttyUSB1'
TTC_SERIAL_BAUD = 19200
TTC_ADDRESS = 17
I2C_address = 0x76


FILE_NAME = "/home/pi/Desktop/Temperature_profile.txt"


class AUTO_PID:
	def main(self):
		print ("start")
		TP = readTempProfile(FILE_NAME)[0]
		print(TP)

		OVEN = TTC4006_Tira.TTC4006(TTC_SERIAL_PORT)

		P = 5
		I = 0
		D = 0

		pid = PID.PID(P, I, D)
		pid.setSampleTime(1)

		t_start = te.time()
		
		for step in TP:
			# setting the oven
			step_time = step[0] * 60  # step_time in seconds
			step_temp = float(format(float(step[1]) / 0.84, ".2f"))
			
			start_time = str(datetime.datetime.now())
			#filename = start_time.replace(" ", "_").replace(".", "-").replace(":", "-") + "_P_5"
			filename = "PID_15" + "_" + start_time.replace(" ", "_").replace(".", "-").replace(":", "-")
			op = open("/home/pi/Desktop/" + filename + ".txt", "a")
			op.write("Time(s)\tSetTemp.(oC)\tActual Temp.(oC)\tTemp.Sensor(oC)\r\n")
			op.close()

			print(step)

			t1 = datetime.datetime.now()
			t2 = datetime.datetime.now() + datetime.timedelta(seconds=step_time)

			while (t1 < t2):
				t_step = te.time()
				t_r = t_step - t_start
				t_run = format(t_r, "0.2f")

				# run oven
				print('01 - Reading data from Oven...')

				t_step = time.time()
				t_r = t_step - t_start
				t_run = format(t_r, "0.2f")
				
				pid.SetPoint = step_temp
				pid.setKp(float(P))
				pid.setKi(float(I))
				pid.setKd(float(D))

				temp_set1 = OVEN.TTC_Read_SP_Temp()
				temp_real1 = OVEN.TTC_Read_PV_Temp()
				temp_set = str(format(temp_set1, "0,.2f"))
				temp_real = str(format(temp_real1, "0,.2f"))
					
				actual_temperature = bme280.readBME280All()[0]

				print("Sensor Temperature : " + str(actual_temperature))

				pid.update(actual_temperature)
				
				target_temperature = pid.output
				
				if target_temperature > 130:
					target_temperature = 130
				elif target_temperature < -40:
					target_temperature = -40
				else:
					target_temperature = target_temperature

				print("PID set Temperature : " +  str(target_temperature))
				print("Chamber real Temperature : " +  temp_real)

				OVEN.TTC_Set_Temp(target_temperature)

				print('Saving data...')
				op = open("/home/pi/Desktop/" + filename + ".txt", "a")
				op.writelines(
					[str(t_run), "\t", str(target_temperature), "\t", temp_real, "\t",str(actual_temperature), "\r\n"])
				op.close()
				
				time.sleep(1)
				
				t1 = datetime.datetime.now()


if __name__ == "__main__":
	PID_VT = AUTO_PID()
	PID_VT.main()

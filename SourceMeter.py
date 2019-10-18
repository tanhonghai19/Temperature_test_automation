import visa

class SourceMeter:
	def __init__(self, addr):
		self.VISA_addr = addr
		self.Channel = ""
		self.fVoltage = float(0)
		self.fMeasuredVoltage = float(0)
		self.fMeasuredCurrent = float(0)
		self.bChannelInitialized = False
		self.bDeviceInitialized = False
		self.CMD_ID = "*IDN?"
		self.instSRC = ""
		self.rm = ""

	def reset(self):
		self.Channel = ""
		self.fVoltage = float(0)
		self.fMeasuredVoltage = float(0)
		self.fMeasuredCurrent = float(0)
		self.bChannelInitialized = False
		self.setV("a", 0)
		self.bChannelInitialized = False
		self.setV("b", 0)
		self.bChannelInitialized = False
		self.Channel = ""

	def GoSafe(self):
		self.reset()
	
	def setChannel(self, ch):
		if ch == "a" or ch == "A":
			self.Channel = "a"
		else:
			self.Channel = "b"

		self.CMD_Function = "smu" + self.Channel + ".source.func = smu" + self.Channel + ".OUTPUT_DCVOLTS"
		self.CMD_VoltageSet = "smu" + self.Channel + ".source.levelv = "
		self.CMD_ChannelON = "smu" + self.Channel + ".source.output = smu" + self.Channel + ".OUTPUT_ON"
		self.CMD_Read_I = "print(smu' + self.Channel + '.measure.i())"
		self.CMD_Read_V = "print(smu' + self.Channel + '.measure.v())"

	def InitDevice(self):
		if self.bDeviceInitialized  == False:
			self.rm = visa.ResourceManager()
			
			#initialize GPIB address of source meter
			self.instSRC = self.rm.open_resource( self.VISA_addr )
			self.instSRC.read_termination = "\n"
			self.bDeviceInitialized = True

	#Intialization for DC voltage
	def InitChannel(self):
		self.InitDevice()
		if self.bChannelInitialized == False:
			self.instSRC.write( self.CMD_Function )
			self.bChannelInitialized = True

	#Write desired voltage
	def setV(self, ch, v):
		self.fVoltage = v
		self.setChannel(ch)
		self.InitChannel()
		self.instSRC.write(self.CMD_VoltageSet + str(self.fVoltage))
		self.instSRC.write(self.CMD_ChannelON)

	#Command to read current and voltage
	def Measure(self, ch, v):
		self.setV(ch, v)
		self.fMeasuredCurrent = float(self.instSRC.query(self.CMD_Read_I))
		self.fMeasuredVoltage = float(self.instSRC.query(self.CMD_Read_V))
		return self.fMeasuredCurrent

	def getInfo(self):
		self.InitDevice()
		return self.instSRC.query(self.CMD_ID)

	def getV(self):
		return self.fMeasuredVoltage

	def getI(self):
		return self.fMeasuredCurrent

	def getR(self):
		return self.fMeasuredVoltage / self.fMeasuredCurrent

	def __str__(self):
		return 'V = %.3f' % self.getV() + ' I = %.3E' % self.getI() + ' R = %.2f' % self.getR()


if __name__ == "__main__":
	SM = SourceMeter('GPIB0::3::INSTR')
	print(SM.getInfo())
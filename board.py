from machine import ADC, Pin

class Board:
	numberMatrix = [[31800]*15 for _ in range(15)]
	calibrationMatrix = [[31800]*15 for _ in range(15)]
	correctedNumberMatrix = [[0]*15 for _ in range(15)]
	stoneMatrix = [[' ']*15 for _ in range(15)]

	BLACK_TRESHOLD = 600
	WHITE_TRESHOLD = 600

	

	def __init__(self):
		self.O = ADC(Pin(26)) # output pin
		self.E = None # enable pin, not used
		
		# Individual mux control pins (S0-S3)
		self.S0 = Pin(10, Pin.OUT)
		self.S1 = Pin(11, Pin.OUT)
		self.S2 = Pin(12, Pin.OUT)
		self.S3 = Pin(13, Pin.OUT)
		
		# Main mux control pins (M0-M3)
		self.M0 = Pin(4, Pin.OUT)
		self.M1 = Pin(5, Pin.OUT)
		self.M2 = Pin(6, Pin.OUT)
		self.M3 = Pin(7, Pin.OUT)

	def updateMatrix(self):
		for i in range(15):
			self.setI(i)
			for j in range(15):
				self.setJ(j)
				self.numberMatrix[i][j] = self.O.read_u16()
				self.correctedNumberMatrix[i][j] = self.numberMatrix[i][j] - self.calibrationMatrix[i][j]
				if self.correctedNumberMatrix[i][j] > self.BLACK_TRESHOLD:
					self.stoneMatrix[i][j] = 'B'
				elif self.correctedNumberMatrix[i][j] < -self.WHITE_TRESHOLD:
					self.stoneMatrix[i][j] = 'W'
				else:
					self.stoneMatrix[i][j] = ' '

	
	def calibrate(self):
		for i in range(15):
			self.setI(i)
			for j in range(15):
				self.setJ(j)
				self.calibrationMatrix[i][j] = self.O.read_u16()
				self.correctedNumberMatrix[i][j] = 0
				self.stoneMatrix[i][j] = ' '

	def setI(self, value):
		# Set individual mux
		self.S0.value(1 if (value & 1) else 0)
		self.S1.value(1 if (value & 2) else 0)
		self.S2.value(1 if (value & 4) else 0)
		self.S3.value(1 if (value & 8) else 0)
		
	def setJ(self, value):
		# Set main mux
		self.M0.value(1 if (value & 1) else 0)
		self.M1.value(1 if (value & 2) else 0)
		self.M2.value(1 if (value & 4) else 0)
		self.M3.value(1 if (value & 8) else 0)

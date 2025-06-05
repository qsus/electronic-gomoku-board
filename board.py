from machine import ADC, Pin
import uasyncio as asyncio

class Board:
	# variable matrices
	numberMatrix = [[31800]*15 for _ in range(15)]
	calibrationMatrix = [[31800]*15 for _ in range(15)]
	# derived matrices
	correctedNumberMatrix = [[0]*15 for _ in range(15)]
	stoneMatrix = [[' ']*15 for _ in range(15)]
	#rotatedStoneMatrix
	#rotatedCorrectedNumberMatrix

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
		
		# Flag to control monitoring loop
		self.monitoring = False
		
		# Stone change observers
		self.stoneObservers = []

	def updateMatrix(self):
		"""Read the current values from the board and update the numberMatrix.
		This takes about 24ms for the reading and in total 70ms including the update of derived matrices.
		"""
		for i in range(15):
			self.setI(i)
			for j in range(15):
				self.setJ(j)
				self.numberMatrix[i][j] = self.O.read_u16()
				
		self.updateDerivedMatrices()

	def updateDerivedMatrices(self):
		"""Update all derived matrices. MUST be called after any change in numberMatrix or calibrationMatrix or tresholds."""
		for i in range(15):
			for j in range(15):
				# Apply calibration correction
				self.correctedNumberMatrix[i][j] = self.numberMatrix[i][j] - self.calibrationMatrix[i][j]

				# Calculate the stone type based on corrected values
				previousStone = self.stoneMatrix[i][j]
				if self.correctedNumberMatrix[i][j] > self.BLACK_TRESHOLD:
					self.stoneMatrix[i][j] = 'B'
				elif self.correctedNumberMatrix[i][j] < -self.WHITE_TRESHOLD:
					self.stoneMatrix[i][j] = 'W'
				else:
					self.stoneMatrix[i][j] = ' '
				
				# If stone changed, notify observers
				if previousStone != self.stoneMatrix[i][j]:
					for observer in self.stoneObservers:
						observer(i, j, previousStone, self.stoneMatrix[i][j])
		

	
	def calibrate(self):
		"""Calibrate the board by reading the current values and setting them as calibration values."""
		for i in range(15):
			self.setI(i)
			for j in range(15):
				self.setJ(j)
				self.calibrationMatrix[i][j] = self.O.read_u16()
				
		self.updateDerivedMatrices()

	def setI(self, value):
		"""Choose columns (change 15 muxes)"""
		self.S0.value(1 if (value & 1) else 0)
		self.S1.value(1 if (value & 2) else 0)
		self.S2.value(1 if (value & 4) else 0)
		self.S3.value(1 if (value & 8) else 0)
		
	def setJ(self, value):
		"""Choose row (main mux)"""
		self.M0.value(1 if (value & 1) else 0)
		self.M1.value(1 if (value & 2) else 0)
		self.M2.value(1 if (value & 4) else 0)
		self.M3.value(1 if (value & 8) else 0)

	async def startMonitoring(self, interval_ms=0):
		"""Start regular board updates at the specified interval."""
		self.monitoring = True
		while self.monitoring:
			#import time
			#start = time.ticks_ms()
			self.updateMatrix()
			#end = time.ticks_ms()
			#print(f"Board updated in {time.ticks_diff(end, start)} ms")
			await asyncio.sleep_ms(interval_ms)
	
	def stopMonitoring(self):
		self.monitoring = False
	
	def stoneUpdate(self, callback):
		"""
		Decorator to register a function as a stone change listener.
		Example usage:
		
		@board.stone_change_listener
		def on_stone_changed(row, col, old_stone, new_stone):
			print(f"Stone at {row},{col} changed from {old_stone} to {new_stone}")
		"""
		if callback not in self.stoneObservers:
			self.stoneObservers.append(callback)
		return callback

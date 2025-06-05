from machine import ADC, Pin
import uasyncio as asyncio
from matrix_transformator import transform_matrix
from config import O, E, S0, S1, S2, S3, M0, M1, M2, M3, BLACK_THRESHOLD, WHITE_THRESHOLD, ROTATION, FLIP

class Board:
	# variable matrices
	number_matrix = [[31800]*15 for _ in range(15)]
	calibration_matrix = [[31800]*15 for _ in range(15)]
	# derived matrices
	corrected_number_matrix = [[0]*15 for _ in range(15)]
	stone_matrix = [[' ']*15 for _ in range(15)]
	rotated_stone_matrix = [[' ']*15 for _ in range(15)]
	rotated_corrected_number_matrix = [[0]*15 for _ in range(15)]

	def __init__(self):
		self.O = ADC(Pin(O)) # output pin
		self.E = E # enable pin, not used
		
		# Individual mux control pins (S0-S3)
		self.S0 = Pin(S0, Pin.OUT)
		self.S1 = Pin(S1, Pin.OUT)
		self.S2 = Pin(S2, Pin.OUT)
		self.S3 = Pin(S3, Pin.OUT)
		
		# Main mux control pins (M0-M3)
		self.M0 = Pin(M0, Pin.OUT)
		self.M1 = Pin(M1, Pin.OUT)
		self.M2 = Pin(M2, Pin.OUT)
		self.M3 = Pin(M3, Pin.OUT)
		
		# Flag to control monitoring loop
		self.monitoring = False
		
		# Stone change observers
		self.stone_observers = []

	def update_matrix(self):
		"""Read the current values from the board and update the number_matrix.
		This takes about 24ms for the reading and in total 70ms including the update of derived matrices.
		"""
		for i in range(15):
			self.set_i(i)
			for j in range(15):
				self.set_j(j)
				self.number_matrix[i][j] = self.O.read_u16()
				
		self.update_derived_matrices()

	def update_derived_matrices(self):
		"""Update all derived matrices. MUST be called after any change in number_matrix or calibration_matrix or tresholds."""
		for i in range(15):
			for j in range(15):
				# Apply calibration correction
				self.corrected_number_matrix[i][j] = self.number_matrix[i][j] - self.calibration_matrix[i][j]

				# Calculate the stone type based on corrected values
				previous_stone = self.stone_matrix[i][j]
				if self.corrected_number_matrix[i][j] > BLACK_THRESHOLD:
					self.stone_matrix[i][j] = 'B'
				elif self.corrected_number_matrix[i][j] < -WHITE_THRESHOLD:
					self.stone_matrix[i][j] = 'W'
				else:
					self.stone_matrix[i][j] = ' '
				
				# If stone changed, notify observers
				if previous_stone != self.stone_matrix[i][j]:
					for observer in self.stone_observers:
						observer(i, j, previous_stone, self.stone_matrix[i][j])

		# Transform matrices
		self.rotated_stone_matrix = transform_matrix(self.stone_matrix, rotation=ROTATION, flip=FLIP)
		self.rotated_corrected_number_matrix = transform_matrix(self.corrected_number_matrix, rotation=ROTATION, flip=FLIP)

		

	
	def calibrate(self):
		"""Calibrate the board by reading the current values and setting them as calibration values."""
		for i in range(15):
			self.set_i(i)
			for j in range(15):
				self.set_j(j)
				self.calibration_matrix[i][j] = self.O.read_u16()
				
		self.update_derived_matrices()

	def set_i(self, value):
		"""Choose columns (change 15 muxes)"""
		self.S0.value(1 if (value & 1) else 0)
		self.S1.value(1 if (value & 2) else 0)
		self.S2.value(1 if (value & 4) else 0)
		self.S3.value(1 if (value & 8) else 0)
		
	def set_j(self, value):
		"""Choose row (main mux)"""
		self.M0.value(1 if (value & 1) else 0)
		self.M1.value(1 if (value & 2) else 0)
		self.M2.value(1 if (value & 4) else 0)
		self.M3.value(1 if (value & 8) else 0)

	async def start_monitoring(self, interval_ms=0):
		"""Start regular board updates at the specified interval."""
		self.monitoring = True
		while self.monitoring:
			#import time
			#start = time.ticks_ms()
			self.update_matrix()
			#end = time.ticks_ms()
			#print(f"Board updated in {time.ticks_diff(end, start)} ms")
			await asyncio.sleep_ms(interval_ms)
	
	def stop_monitoring(self):
		self.monitoring = False
	
	def stone_update(self, callback):
		"""
		Decorator to register a function as a stone change listener.
		Example usage:
		
		@board.stone_change_listener
		def on_stone_changed(row, col, old_stone, new_stone):
			print(f"Stone at {row},{col} changed from {old_stone} to {new_stone}")
		"""
		if callback not in self.stone_observers:
			self.stone_observers.append(callback)
		return callback

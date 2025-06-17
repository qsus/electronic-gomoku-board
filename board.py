from machine import ADC, Pin
import uasyncio as asyncio
from config import O, E, S0, S1, S2, S3, M0, M1, M2, M3, BLACK_THRESHOLD, WHITE_THRESHOLD, ROTATION, FLIP, D_TIMINGS
import time
import rp2
import micropython

class Board:
	def __init__(self):
		# matrices
		self.number_matrix = [[31800]*15 for _ in range(15)]
		self.calibration_matrix = [[31800]*15 for _ in range(15)]
		self.stone_matrix = [[' ']*15 for _ in range(15)]

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
		self.changed_stones = []


		self.GRAY_CODE_S = [  # write value to S and the output is index j
			(0b0001, self.S0, 1), (0b0011, self.S1, 1), (0b0010, self.S0, 0), (0b0110, self.S2, 1),
			(0b0111, self.S0, 1), (0b0101, self.S1, 0),	(0b0100, self.S0, 0), (0b1100, self.S3, 1),
			(0b1101, self.S0, 1), (0b1111, self.S1, 1),	(0b1110, self.S0, 0), (0b1010, self.S2, 0),
			(0b1011, self.S0, 1), (0b1001, self.S1, 0),	(0b1000, self.S0, 0), (0b0000, self.S3, 0),
		]
		self.GRAY_CODE_M = [  # write value to M and the output is index j
			(0b0001, self.M0, 1), (0b0011, self.M1, 1), (0b0010, self.M0, 0), (0b0110, self.M2, 1),
			(0b0111, self.M0, 1), (0b0101, self.M1, 0),	(0b0100, self.M0, 0), (0b1100, self.M3, 1),
			(0b1101, self.M0, 1), (0b1111, self.M1, 1),	(0b1110, self.M0, 0), (0b1010, self.M2, 0),
			(0b1011, self.M0, 1), (0b1001, self.M1, 0),	(0b1000, self.M0, 0), (0b0000, self.M3, 0),
		]


	
	@micropython.native
	def update_matrix(self, calibrate=False):
		"""Read the current values from the board and update the number_matrix."""
		# Reset all mux to 0
		for mux in [self.M0, self.M1, self.M2, self.M3, self.S0, self.S1, self.S2, self.S3]:
			mux.value(0)

		for i, S, value in self.GRAY_CODE_S:
			# set value and ensure not out of range
			S.value(value)
			if i >= 15:
				continue

			for j, M, value in self.GRAY_CODE_M:
				# set value and ensure not out of range
				M.value(value)
				if j >= 15:
					continue

				# Based on rotation and flip, adjust the indices
				if ROTATION == 0:
					x, y = 14 - i, 14 - j
				elif ROTATION == 1:
					x, y = j, 14 - i
				elif ROTATION == 2:
					x, y = i, j
				elif ROTATION == 3:
					x, y = 14 - j, i
				if FLIP:
					x, y = 14 - x, y
				
				# Read the value from the ADC and correct it with the calibration matrix
				if calibrate:
					self.calibration_matrix[x][y] = self.O.read_u16()
				else:
					self.number_matrix[x][y] = self.O.read_u16() - self.calibration_matrix[x][y] # 30 us

				# Calculate the stone type based on corrected values
				previous_stone = self.stone_matrix[x][y]
				if self.number_matrix[x][y] > BLACK_THRESHOLD:
					self.stone_matrix[x][y] = 'B'
				elif self.number_matrix[x][y] < -WHITE_THRESHOLD:
					self.stone_matrix[x][y] = 'W'
				else:
					self.stone_matrix[x][y] = ' '

				# Notify observers if the stone has changed
				if previous_stone != self.stone_matrix[x][y]:
					self.changed_stones.append((x, y, previous_stone, self.stone_matrix[x][y]))
	
	def calibrate(self):
		"""Calibrate the board by reading the current values and setting them as calibration values."""
		self.update_matrix(calibrate=True)

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
			t0 = time.ticks_us()
			self.update_matrix()
			t1 = time.ticks_us()
			if D_TIMINGS:
				print(time.ticks_diff(t1, t0), end='m ')
			
			# Notify observers about changed stones
			while self.changed_stones:
				x, y, previous_stone, new_stone = self.changed_stones.pop(0)
				for observer in self.stone_observers:
					await observer(x, y, previous_stone, new_stone)

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

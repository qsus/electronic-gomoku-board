from machine import ADC, Pin
import uasyncio as asyncio
from matrix_transformator import transform_matrix
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

		@rp2.asm_pio(out_init=[rp2.PIO.OUT_LOW] * 4)
		def asm_mux_writer():
			wrap_target()                           # type: ignore
			pull() # FIFO > OSR; one word = 32 bits # type: ignore
			out(pins, 4) # OSR > pins; 4 bits       # type: ignore
			push(noblock)                           # type: ignore
			wrap()                                  # type: ignore
		
		self.sm_mux_i = rp2.StateMachine(0, asm_mux_writer, out_base=Pin(S0), out_shiftdir=rp2.PIO.SHIFT_RIGHT) # type: ignore
		self.sm_mux_i.active(1)
		self.sm_mux_j = rp2.StateMachine(1, asm_mux_writer, out_base=Pin(M0), out_shiftdir=rp2.PIO.SHIFT_RIGHT) # type: ignore
		self.sm_mux_j.active(1)
	
	@micropython.native
	def update_matrix(self):
		"""Read the current values from the board and update the number_matrix."""
		# Time to run the whole function in ms:
		# without assembly: 19 or 27 if called from function
		# with assembly:    13 or 21 if called from function
		# Timings after each command aren't relevant because they add up to lower numbers
		for i in range(15):
			self.sm_mux_i.put(i) # 30 us
			self.sm_mux_i.get()  # 30 us both commands
			# TODO: rotation here
			for j in range(15):				
				self.sm_mux_j.put(j) # 30 us
				self.sm_mux_j.get()  # 30 us both commands
				
				# Read the value from the ADC and correct it with the calibration matrix
				self.number_matrix[i][j] = self.O.read_u16() - self.calibration_matrix[i][j] # 30 us

				# Calculate the stone type based on corrected values
				previous_stone = self.stone_matrix[i][j]
				if self.number_matrix[i][j] > BLACK_THRESHOLD:
					self.stone_matrix[i][j] = 'B'
				elif self.number_matrix[i][j] < -WHITE_THRESHOLD:
					self.stone_matrix[i][j] = 'W'
				else:
					self.stone_matrix[i][j] = ' '

				# Notify observers if the stone has changed
				if previous_stone != self.stone_matrix[i][j]:
					self.changed_stones.append((i, j, previous_stone, self.stone_matrix[i][j]))
	
	def calibrate(self):
		"""Calibrate the board by reading the current values and setting them as calibration values."""
		for i in range(15):
			self.sm_mux_i.put(i)
			self.sm_mux_i.get()
			for j in range(15):
				self.sm_mux_j.put(j)
				self.sm_mux_j.get()
				self.calibration_matrix[i][j] = self.O.read_u16()

	def set_i(self, value):
		"""Choose columns (change 15 muxes)"""
		self.sm_mux_i.put(value)
		self.sm_mux_i.get()
		return
		self.S0.value(1 if (value & 1) else 0)
		self.S1.value(1 if (value & 2) else 0)
		self.S2.value(1 if (value & 4) else 0)
		self.S3.value(1 if (value & 8) else 0)
		
	def set_j(self, value):
		"""Choose row (main mux)"""
		self.sm_mux_j.put(value)
		self.sm_mux_j.get()
		return
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
				i, j, previous_stone, new_stone = self.changed_stones.pop(0)
				for observer in self.stone_observers:
					await observer(i, j, previous_stone, new_stone)

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

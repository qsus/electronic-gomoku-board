from config import DEBOUNCE_TIME
from machine import Pin
from time import ticks_ms, ticks_diff
import asyncio

class Button:
	def __init__(self, pin_id, callback = lambda: None):
		self.pin = Pin(pin_id, Pin.IN, Pin.PULL_UP)
		self._last_press = ticks_ms()
		self.callback = callback
		asyncio.create_task(self._loop()) # Start the asynchronous loop
		self.has_been_released = True # Used in case asyncio caused too large delay

	async def _loop(self):
		"""Asynchronous loop to check the button state."""
		while True:
			if self.pin.value() == 0: # If pressed
				# Reset last press and calculate difference
				last = self._last_press
				self._last_press = ticks_ms()
				diff_time = ticks_diff(self._last_press, last)
				if diff_time > DEBOUNCE_TIME and self.has_been_released: # If hasn't been pressed recently
					self.callback()
					self.has_been_released = False
			else:
				self.has_been_released = True
			await asyncio.sleep(0.01) # yield

	def set_callback(self, callback):
		self.callback = callback

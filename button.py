from config import DEBOUNCE_TIME
from machine import Pin
from time import ticks_ms, ticks_diff

class Button:
	def __init__(self, pin_id, callback = None):
		self.pin = Pin(pin_id, Pin.IN, Pin.PULL_UP)
		self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self._press)
		self._last_press = ticks_ms()
		self.callback = callback

	def set_callback(self, callback):
		"""Set a callback function to be called when the button is pressed."""
		self.callback = callback

	def _press(self, pin):
		# Debounce logic
		last = self._last_press
		self._last_press = ticks_ms()
		diff_time = ticks_diff(self._last_press, last)
		if diff_time < DEBOUNCE_TIME:
			return
		# If button is pressed, call the callback if it exists
		if pin.value() == 0 and self.callback:
			self.callback()

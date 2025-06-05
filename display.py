from machine import Pin
import time
from config import DEBOUNCE_TIME, MAIN_BUTTON_PIN, LEFT_BUTTON_PIN, RIGHT_BUTTON_PIN, SCL, SDA
from lcd_i2c import I2cLcd
from machine import I2C

class Display:
	menu = [
		("Main", lambda: print("Main menu selected")),
		("Set station mode", lambda: print("Set station mode selected")),
		("Set client mode", lambda: print("Set access point mode selected")),
		("Calibrate", lambda: print("Calibration selected")),
	]
	menu_index = 0

	def __init__(self):
		self.button_left = Pin(LEFT_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
		self.button_main = Pin(MAIN_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
		self.button_right = Pin(RIGHT_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
		self.button_left.irq(trigger=Pin.IRQ_FALLING, handler=self._button_press)
		self.button_main.irq(trigger=Pin.IRQ_FALLING, handler=self._button_press)
		self.button_right.irq(trigger=Pin.IRQ_FALLING, handler=self._button_press)
		self.button_left_last = time.ticks_ms()
		self.button_main_last = time.ticks_ms()
		self.button_right_last = time.ticks_ms()
		self.i2c = I2C(1, scl=Pin(SCL), sda=Pin(SDA))
		self.lcd = I2cLcd(self.i2c, 0x27)
		self._print_menu()

	def _button_press(self, pin):
		if pin == self.button_left:
			last = self.button_left_last
			self.button_left_last = time.ticks_ms()
			action = self._button_left
		elif pin == self.button_main:
			last = self.button_main_last
			self.button_main_last = time.ticks_ms()
			action = self._button_main
		elif pin == self.button_right:
			last = self.button_right_last
			self.button_right_last = time.ticks_ms()
			action = self._button_right
		else:
			return
		# debounce logic; note that button RELEASE might get ignored
		# operates using time difference
		diff_time = time.ticks_diff(time.ticks_ms(), last)
		if diff_time < DEBOUNCE_TIME:
			return
		if pin.value() == 1:
			return
		action() # Call the appropriate button action method
		
	def _button_left(self):
		self.menu_index -= 1
		self.menu_index %= len(self.menu)
		self._print_menu()
		
	def _button_main(self):
		self.menu[self.menu_index][1]()

	def _button_right(self):
		self.menu_index += 1
		self.menu_index %= len(self.menu)
		self._print_menu()

	def _print_menu(self):
		self.lcd.clear()
		self.lcd.move_to(0, 0)
		self.lcd.putstr(self.menu[self.menu_index][0])

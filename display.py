from machine import Pin
import time
from config import DEBOUNCE_TIME, MAIN_BUTTON_PIN, LEFT_BUTTON_PIN, RIGHT_BUTTON_PIN, SCL, SDA
from lcd_i2c import I2cLcd
from machine import I2C

class Display:
	DISPLAY_MODE_MENU = 0
	DISPLAY_MODE_SPLASH = 1
	DISPLAY_MODE_CLOCK = 2

	menu = [
		("Welcome to ECB!", lambda: print("Main menu selected")),
	]
	menu_index = 0
	
	display_mode = DISPLAY_MODE_MENU

	def add_menu_item(self, label):
		"""A decorator to add a menu item with the given label.

		Usage example:

		@display.add_menu_item("Item label")
		def my_function():
			# Function code here
		"""
		def decorator(func):
			self.menu.append((label, func))
			return func
		return decorator

	def show_splash(self, line1 = None, line2 = None):
		self.display_mode = self.DISPLAY_MODE_SPLASH
		if line1:
			self.lcd.move_to(0, 0)
			self.lcd.putstr(line1)
			self.lcd.putstr(" " * (16 - len(line1)))
		if line2:
			self.lcd.move_to(0, 1)
			self.lcd.putstr(line2)
			self.lcd.putstr(" " * (16 - len(line2)))

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
		if self.display_mode == self.DISPLAY_MODE_MENU: # Execute action
			self.menu[self.menu_index][1]()
		elif self.display_mode == self.DISPLAY_MODE_SPLASH: # Go back to menu
			self.display_mode = self.DISPLAY_MODE_MENU
			self._print_menu()
		elif self.display_mode == self.DISPLAY_MODE_CLOCK: # TODO: Implement clock mode
			pass

	def _button_right(self):
		self.menu_index += 1
		self.menu_index %= len(self.menu)
		self._print_menu()

	def _print_menu(self):
		self.lcd.clear()
		self.lcd.move_to(0, 0)
		self.lcd.putstr(self.menu[self.menu_index][0])

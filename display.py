from machine import Pin
from config import SCL, SDA
from lcd_i2c import I2cLcd
from machine import I2C
from clock import Clock

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
		self.i2c = I2C(1, scl=Pin(SCL), sda=Pin(SDA))
		self.lcd = I2cLcd(self.i2c, 0x27)
		self._print_menu()

	def clock_update(self, clock: Clock):
		"""Observer method to update the display with the clock message."""
		message  = f"{clock.time_left[0] // 3600000}:{(clock.time_left[0] // 60000) % 60:02}:{(clock.time_left[0] // 1000) % 60:02}"
		# H:MM:SS
		
		if clock.win == clock.PLAYER_1:
			statusSignal = "WL"
		elif clock.win == clock.PLAYER_2:
			statusSignal = "LW"
		else:
			statusSignal = "  "

		if clock.running and clock.turn == clock.PLAYER_1:
			statusSignal = '*' + statusSignal[1]
		elif clock.running and clock.turn == clock.PLAYER_2:
			statusSignal = statusSignal[0] + '*'
		# WL, LW, or "  ", overlayed with * if running

		message += statusSignal
		message += f"{clock.time_left[1] // 3600000}:{(clock.time_left[1] // 60000) % 60:02}:{(clock.time_left[1] // 1000) % 60:02}"
		# H:MM:SS  H:MM:SS (with status signal in the middle)

		self.lcd.move_to(0, 1)
		self.lcd.putstr(message)
		
		
	def menu_left(self):
		self.menu_index -= 1
		self.menu_index %= len(self.menu)
		self._print_menu()
		
	def menu_select(self):
		if self.display_mode == self.DISPLAY_MODE_MENU: # Execute action
			self.menu[self.menu_index][1]()
		elif self.display_mode == self.DISPLAY_MODE_SPLASH: # Go back to menu
			self.display_mode = self.DISPLAY_MODE_MENU

	def menu_right(self):
		self.menu_index += 1
		self.menu_index %= len(self.menu)
		self._print_menu()

	def _print_menu(self):
		self.lcd.clear()
		self.lcd.move_to(0, 0)
		self.lcd.putstr(self.menu[self.menu_index][0])

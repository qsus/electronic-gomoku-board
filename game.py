from clock import Clock

class Game:
	def __init__(self, display, board):
		self.display = display
		self.board = board
		self.clock = Clock()
		self.clock.init_clock()
		
		self.clock.add_observer(lambda clock: self.drawLcd())

	def drawLcd(self):
		"""Observer method to update the display with the clock message."""
		clock = self.clock

		message  = f"{clock.time_left[0] // 3600000}:{(clock.time_left[0] // 60000) % 60:02}:{(clock.time_left[0] // 1000) % 60:02}"
		# H:MM:SS
		
		if clock.win == clock.PLAYER_1:
			statusSignal = "WL"
		elif clock.win == clock.PLAYER_2:
			statusSignal = "LW"
		else:
			statusSignal = "  "

		# if running, show * even if game ended; if paused and not ended, show .
		if clock.running and clock.turn == clock.PLAYER_1:
			statusSignal = '*' + statusSignal[1]
		elif clock.running and clock.turn == clock.PLAYER_2:
			statusSignal = statusSignal[0] + '*'
		elif clock.win is None and clock.turn == clock.PLAYER_1:
			statusSignal = '.' + statusSignal[1]
		elif clock.win is None and clock.turn == clock.PLAYER_2:
			statusSignal = statusSignal[0] + '.'
		# WL, LW, or "  ", overlayed with * if running

		message += statusSignal
		message += f"{clock.time_left[1] // 3600000}:{(clock.time_left[1] // 60000) % 60:02}:{(clock.time_left[1] // 1000) % 60:02}"
		# H:MM:SS  H:MM:SS (with status signal in the middle)

		heading = "Game in progress" if clock.running else "Game paused"
		self.display.show_splash(heading, message)

	def pauseUnpause(self):
		"""Pause or unpause the clock."""
		if self.clock.running:
			self.clock.pause()
		else:
			self.clock.unpause()

	def button1(self):
		self.clock.button1()

	def button2(self):
		self.clock.button2()
		
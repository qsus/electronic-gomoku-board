import asyncio
import time

class Clock:
	PLAYER_1 = 0
	PLAYER_2 = 1

	observers = set()

	def add_observer(self, observer):
		self.observers.add(observer)

	def send_update(self):
		for observer in self.observers:
			observer(self)

	def __init__(self):
		self.running = False
		asyncio.create_task(self._async_loop())

	def init_clock(self, time1 = 3 * 60, time2 = 3 * 60, fisher1 = 0, fisher2 = 0):
		self.fisher1 = fisher1
		self.fisher2 = fisher2

		self.running = False
		self.turn = self.PLAYER_1
		self.win = None
		self.fisher = [fisher1 * 1000, fisher2 * 1000]
		self.time_left = [time1 * 1000, time2 * 1000]

	async def _async_loop(self):
		while True:
			if not self.running:
				await asyncio.sleep(0.1)
				continue

			self._apply_elapsed()

			# wait until XX:XX.00
			sleep_time = self.time_left[self.turn] % 1000 / 1000.0

			await asyncio.sleep(sleep_time)

	def _apply_elapsed(self):
		"""Remove elapsed time from the current player's clock. Can be safely called at any time. Must be called before player switch and should be called periodically."""
		if not self.running:
			return

		now = time.ticks_ms()
		elapsed = time.ticks_diff(now, self.last_switch_time)
		self.last_switch_time = now

		self.time_left[self.turn] -= elapsed
		if self.time_left[self.turn] < 0:
			self.time_left[self.turn] = 0
			self.win = self.PLAYER_2 if self.turn == self.PLAYER_1 else self.PLAYER_1
			self.running = False
			
		self.send_update()
	
	def pause(self):
		self._apply_elapsed()
		self.running = False
		self.send_update()

	def unpause(self):
		self.running = True
		self.last_switch_time = time.ticks_ms()
		self.send_update()

	def button1(self):
		self._apply_elapsed()
		self.turn = 1
		self.send_update()

	def button2(self):
		self._apply_elapsed()
		self.turn = 0
		self.send_update()

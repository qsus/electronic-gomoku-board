from microdot import Microdot, send_file, Request, websocket
from microdot.websocket import with_websocket
import asyncio
import json
from board import Board
import network
import time

class Server:
	def __init__(self, board: Board):
		self.board = board
		self.app = Microdot()
		self.websockets = set()
		
		self.app.route('/')(self.indexHandler)
		self.app.route('/ws')(with_websocket(self.wsHandler))
		

	async def start(self, ssid=None, password=None, port=80):
		if ssid and password:
			self.wifiConnectBlocking(ssid, password)
			print(f"Connected to WiFi: {self.networkInfo}")
		else:
			print("No WiFi credentials provided, running possibly offline.")
		await self.app.start_server(port=port)

	async def indexHandler(self, request: Request):
		return send_file('static/index.html', content_type='text/html')
	
	async def wsHandler(self, request: Request, ws: websocket.WebSocket):
		self.websockets.add(ws)
		await ws.send(json.dumps({
			'type': 'fullBoard',
			'board': self.board.stoneMatrix,
		}))
		while True:
			# recieve and send loop; aditional messages can be sent outside this loop
			if ws.closed:
				self.websockets.remove(ws)
				break
			message = await ws.receive()
			await ws.send(message)

	async def sendToAll(self, message):
		for ws in self.websockets:
			if not ws.closed:
				try:
					await ws.send(message)
				except Exception as e:
					print(f"Error sending update: {e}")

	def wifiConnectBlocking(self, ssid, password):
		wlan = network.WLAN(network.STA_IF)
		wlan.active(True)
		wlan.config(pm=0) # disable power saving - it would introduce delays in seconds
		wlan.connect(ssid, password)
		while not wlan.isconnected():
			time.sleep(1)		
		self.networkInfo = wlan.ifconfig()

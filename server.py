from microdot import Microdot, send_file, Request, websocket
from microdot.websocket import with_websocket
import asyncio
import json
from board import Board
from config import PORT

class Server:
	def __init__(self, board: Board):
		self.board = board
		self.app = Microdot()
		self.websockets = set()
		
		self.app.route('/')(self.index_handler)
		self.app.route('/ws')(with_websocket(self.ws_handler))
		

	async def start(self, port=80):
		await self.app.start_server(port=port)

	async def index_handler(self, request: Request):
		return send_file('static/index.html', content_type='text/html')
	
	async def ws_handler(self, request: Request, ws: websocket.WebSocket):
		self.websockets.add(ws)
		await ws.send(json.dumps({
			'type': 'full_board',
			'board': self.board.stone_matrix,
		}))
		while True:
			# recieve and send loop; aditional messages can be sent outside this loop
			if ws.closed:
				self.websockets.remove(ws)
				break
			message = await ws.receive()
			await ws.send(message)

	async def send_to_all(self, message):
		for ws in self.websockets:
			if not ws.closed:
				try:
					await ws.send(message)
				except Exception as e:
					print(f"Error sending update: {e}")

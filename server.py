from microdot import Microdot, send_file, Request, websocket
from microdot.websocket import with_websocket
import json
from board import Board
from machine import soft_reset
from config import PORT

class Server:
	def __init__(self, board: Board):
		self.board = board
		self.app = Microdot()
		self.websockets = set()
		
		self.app.route('/')(self.index_handler)
		self.app.route('/ws')(with_websocket(self.ws_handler))
		self.app.route('/config')(self.config_handler)
		self.app.route('/config.py', methods=['GET'])(self.get_settings_handler)
		self.app.route('/config.py', methods=['POST'])(self.post_settings_handler)
		self.app.route('/reset')(lambda request: soft_reset())
		

	async def start(self):
		await self.app.start_server(port=PORT)

	async def index_handler(self, request: Request):
		return send_file('static/index.html', content_type='text/html')
	
	async def config_handler(self, request: Request):
		return send_file('static/config.html', content_type='text/html')
	
	async def get_settings_handler(self, request: Request):
		return send_file('config.py', content_type='text/plain')
	
	async def post_settings_handler(self, request: Request):
		print("Received settings update")
		if request.body is None:
			return "No data received", 400
		body = request.body.decode('utf-8')
		if len(body) < 3: # basic check for empty data
			return "No data received", 400
		
		with open('config.py', 'w') as f:
			f.write(body)
			return "Settings updated successfully", 200

	
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

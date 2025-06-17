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
		
		self.app.route('/live')(with_websocket(self.ws_handler))
		self.app.route('/config', methods=['GET'])(self.get_settings_handler)
		self.app.route('/configDefault', methods=['GET'])(self.get_default_settings_handler)
		self.app.route('/config', methods=['POST'])(self.post_settings_handler)
		self.app.route('/reset')(lambda request: soft_reset())
		self.app.route('/')(self.index_handler)
		self.app.route('/<path:path>')(self.static_handler)
		

	async def start(self):
		await self.app.start_server(port=PORT)

	async def index_handler(self, request: Request):
		return send_file('static/index.html', content_type='text/html')

	async def static_handler(self, request: Request, path: str):
		# get content type
		if path.endswith('.html'):
			content_type = 'text/html'
		elif path.endswith('.js'):
			content_type = 'application/javascript'
		elif path.endswith('.css'):
			content_type = 'text/css'
		elif path.endswith('.png'):
			content_type = 'image/png'
		else:
			content_type = 'text/plain'
		# check if file exists
		try:
			with open(f'static/{path}', 'rb') as f:
				pass
		except OSError:
			return "File not found", 404
		# send file
		return send_file(f'static/{path}', content_type=content_type)
	
	async def get_settings_handler(self, request: Request):
		return send_file('config.py', content_type='text/plain')
	
	async def get_default_settings_handler(self, request: Request):
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

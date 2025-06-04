from microdot import Microdot, send_file, Request, websocket
from microdot.websocket import with_websocket
import asyncio
from board import Board
import json

from main import wifiConnect
wifiConnect()
app = Microdot()


@app.route('/')
async def index(request: Request):
    return send_file('static/index.html', content_type='text/html')

@app.route('/ws')
@with_websocket
async def ws(request, ws: websocket.WebSocket):
    while True:
        message = await ws.receive()
        board.updateMatrix()
        await ws.send(json.dumps(board.stoneMatrix))


board = Board()
board.calibrate()


# run server
async def main():
    print("Starting web server...")
    server = asyncio.create_task(app.start_server(port=80))
    await server

asyncio.run(main())

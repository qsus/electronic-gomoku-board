from microdot import Microdot, send_file, Request, websocket
from microdot.websocket import with_websocket
import asyncio
from board import Board
import json

from main import wifiConnect
wifiConnect()
app = Microdot()

websockets = set()

@app.route('/')
async def index(request: Request):
    return send_file('static/index.html', content_type='text/html')

@app.route('/ws')
@with_websocket
async def ws(request, ws: websocket.WebSocket):
    websockets.add(ws)
    while True:
        message = await ws.receive()
        await ws.send(json.dumps(board.stoneMatrix))


board = Board()
board.calibrate()

@board.stoneUpdate
def stoneUpdate(i, j, previous_stone, new_stone):
    print(f'Stone changed at ({i}, {j}): {previous_stone} -> {new_stone}')
    for ws in websockets:
        if not ws.closed:
            try:
                print(f'Sending update to websocket {ws}')
                asyncio.create_task(ws.send(json.dumps({'row': i, 'col': j, 'stone': new_stone}))) 
            except Exception as e:
                print(f"Error sending update: {e}")
    

# run server
async def main():
    print("Starting web server...")
    asyncio.create_task(board.startMonitoring())
    server = asyncio.create_task(app.start_server(port=80))
    await server

asyncio.run(main())

from microdot import Microdot, send_file, Request, websocket
from microdot.websocket import with_websocket
import asyncio
from board import Board
import json
from server import Server
from secret import SSID, PASSWORD

board = Board()
board.calibrate()
asyncio.create_task(board.startMonitoring())

server = Server(board)
server.start(ssid=SSID, password=PASSWORD, port=80)

@board.stoneUpdate
def stoneUpdate(i, j, previous_stone, new_stone):
    print(f'Stone changed at ({i}, {j}): {previous_stone} -> {new_stone}')
    asyncio.create_task(server.sendToAll({
        'type': 'stoneUpdate',
        'row': i, 'col': j, 'stone': new_stone
    }))


from microdot import Microdot, send_file, Request, websocket
from microdot.websocket import with_websocket
import asyncio
from board import Board
import json
from server import Server
from secret import SSID, PASSWORD
from display import Display

from lcd_i2c import I2cLcd
from machine import Pin, I2C


board = Board()
board.calibrate()

display = Display()

server = Server(board)

@board.stone_update
def stone_update(i, j, previous_stone, new_stone):
    asyncio.create_task(server.send_to_all(json.dumps({
        'type': 'stone_update',
        'row': i, 'col': j, 'stone': new_stone
    })))

async def main():
    # Create tasks to run concurrently
    server_task = asyncio.create_task(server.start(ssid=SSID, password=PASSWORD, port=80))
    board_task = asyncio.create_task(board.start_monitoring())
    
    # Wait for both tasks indefinitely
    await asyncio.gather(server_task, board_task)

asyncio.run(main())

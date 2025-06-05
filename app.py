from microdot import Microdot, send_file, Request, websocket
from microdot.websocket import with_websocket
import asyncio
from board import Board
import json
from server import Server
from secret import SSID, PASSWORD

from lcd.i2c_lcd import Display
from machine import Pin, I2C

i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=100000)
print("I2C dvices:", i2c.scan())  # Vypíše seznam adres nalezených zařízení
lcd = Display(i2c)
lcd.clear()
lcd.write("Go Game Server")

board = Board()
board.calibrate()

server = Server(board)

@board.stoneUpdate
def stoneUpdate(i, j, previous_stone, new_stone):
    asyncio.create_task(server.sendToAll(json.dumps({
        'type': 'stoneUpdate',
        'row': i, 'col': j, 'stone': new_stone
    })))

async def main():
    # Create tasks to run concurrently
    server_task = asyncio.create_task(server.start(ssid=SSID, password=PASSWORD, port=80))
    board_task = asyncio.create_task(board.startMonitoring())
    
    # Wait for both tasks indefinitely
    await asyncio.gather(server_task, board_task)

asyncio.run(main())

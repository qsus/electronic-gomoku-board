import asyncio
from board import Board
import json
from server import Server
from display import Display
from wifi import WifiConnection
from button import Button
from config import LEFT_BUTTON_PIN, MAIN_BUTTON_PIN, RIGHT_BUTTON_PIN, SSID, AP_SSID, AP_PASSWORD, D_TIMINGS
import gc
import time
from game import Game

class App:
    MODE_MENU = 0
    MODE_GAME = 1

    def __init__(self):
        self.board = Board()
        self.board.calibrate()
        self.wifi_connection = WifiConnection()
        self.display = Display()
        self.server = Server(self.board)
        self.button_left = Button(LEFT_BUTTON_PIN, self._left_button_press)
        self.button_main = Button(MAIN_BUTTON_PIN, self._main_button_press)
        self.button_right = Button(RIGHT_BUTTON_PIN, self._right_button_press)
        self.mode = self.MODE_MENU
        self.game = Game(self.display, self.board)
        
        if D_TIMINGS:
            self.last_loop_start = 0
            async def loop_measure():
                """Measure the duration of the main loop."""
                while True:
                    last = self.last_loop_start
                    now = time.ticks_ms()
                    self.last_loop_start = now
                    print(time.ticks_diff(now, last), end='l ')
                    await asyncio.sleep(0)
            asyncio.create_task(loop_measure())
        
        @self.display.add_menu_item("Welcome to ECB!")
        def print_debug():
            print("Debug information:")
            gc.collect()
            free = gc.mem_free()
            allocated = gc.mem_alloc()
            total = free + allocated
            print(f"Memory: {allocated}/{total} ({allocated / total * 100}%) allocated, {free} free")

        @self.display.add_menu_item("Enter game")
        def enter_game():
            self.mode = self.MODE_GAME
            self.game.drawLcd()

        @self.display.add_menu_item("Connect to WiFi")
        def set_client_mode():
            self.wifi_connection.set_client()
            self.display.show_splash("Connecting to:", SSID)

        @self.display.add_menu_item("Set AP mode")
        def set_ap_mode():
            self.wifi_connection.set_ap()
            self.display.show_splash("SSID: " + AP_SSID, "PASS: " + AP_PASSWORD)

        @self.display.add_menu_item("Show IP")
        def show_ip():
            mode = self.wifi_connection.get_mode()
            ip = self.wifi_connection.get_ip()
            self.display.show_splash(mode, ip or "Error")


        @self.board.stone_update
        async def stone_update(i, j, previous_stone, new_stone):
            await self.server.send_to_all(json.dumps({
                'type': 'stone_update',
                'x': i, 'y': j, 'stone': new_stone
            }))

    def _left_button_press(self):
        if self.mode == self.MODE_MENU:
            self.display.menu_left()
        elif self.mode == self.MODE_GAME:
            self.game.button1()

    def _main_button_press(self):
        if self.mode == self.MODE_MENU:
            self.display.menu_select()
        elif self.mode == self.MODE_GAME:
            self.game.pauseUnpause()

    def _right_button_press(self):
        if self.mode == self.MODE_MENU:
            self.display.menu_right()
        elif self.mode == self.MODE_GAME:
            self.game.button2()

    async def main(self):
        # Create tasks to run concurrently
        server_task = asyncio.create_task(self.server.start())
        board_task = asyncio.create_task(self.board.start_monitoring())
        
        # Wait for both tasks indefinitely
        await asyncio.gather(server_task, board_task)

if __name__ == "__main__":
    print("Starting app...")
    app = App()
    asyncio.run(app.main())

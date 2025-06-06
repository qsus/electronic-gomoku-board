import asyncio
from board import Board
import json
from server import Server
from secret import SSID, PASSWORD, AP_SSID, AP_PASSWORD
from display import Display
from wifi import WifiConnection
from clock import Clock
from button import Button
from config import LEFT_BUTTON_PIN, MAIN_BUTTON_PIN, RIGHT_BUTTON_PIN
import gc
import time

class App:
    MODE_MENU = 0
    MODE_CLOCK = 1

    def __init__(self):
        self.board = Board()
        asyncio.create_task(self.board.calibrate())
        self.wifi_connection = WifiConnection()
        self.display = Display()
        self.server = Server(self.board)
        self.clock = Clock()
        self.button_left = Button(LEFT_BUTTON_PIN, self._left_button_press)
        self.button_main = Button(MAIN_BUTTON_PIN, self._main_button_press)
        self.button_right = Button(RIGHT_BUTTON_PIN, self._right_button_press)
        self.mode = self.MODE_MENU

        @self.clock.add_observer
        def clock_update(clock: Clock):
            """Observer method to update the display with the clock message."""
            message  = f"{clock.time_left[0] // 3600000}:{(clock.time_left[0] // 60000) % 60:02}:{(clock.time_left[0] // 1000) % 60:02}"
            # H:MM:SS
            
            if clock.win == clock.PLAYER_1:
                statusSignal = "WL"
            elif clock.win == clock.PLAYER_2:
                statusSignal = "LW"
            else:
                statusSignal = "  "

            if clock.running and clock.turn == clock.PLAYER_1:
                statusSignal = '*' + statusSignal[1]
            elif clock.running and clock.turn == clock.PLAYER_2:
                statusSignal = statusSignal[0] + '*'
            # WL, LW, or "  ", overlayed with * if running

            message += statusSignal
            message += f"{clock.time_left[1] // 3600000}:{(clock.time_left[1] // 60000) % 60:02}:{(clock.time_left[1] // 1000) % 60:02}"
            # H:MM:SS  H:MM:SS (with status signal in the middle)

            self.display.show_splash("Game in progress", message)
        
        @self.display.add_menu_item("Welcome to ECB!")
        def print_debug():
            print("Debug information:")
            gc.collect()
            free = gc.mem_free()
            allocated = gc.mem_alloc()
            total = free + allocated
            print(f"Memory: {allocated}/{total} ({allocated / total * 100}%) allocated, {free} free")

        @self.display.add_menu_item("Start game")
        def start_game():
            self.mode = self.MODE_CLOCK
            self.clock.init_clock()
            self.clock.toggle_running()

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
        def stone_update(i, j, previous_stone, new_stone):
            asyncio.create_task(self.server.send_to_all(json.dumps({
                'type': 'stone_update',
                'row': i, 'col': j, 'stone': new_stone
            })))

    def _left_button_press(self):
        if self.mode == self.MODE_MENU:
            self.display.menu_left()
        elif self.mode == self.MODE_CLOCK:
            self.clock.button1()

    def _main_button_press(self):
        if self.mode == self.MODE_MENU:
            self.display.menu_select()
        elif self.mode == self.MODE_CLOCK:
            self.clock.toggle_running()

    def _right_button_press(self):
        if self.mode == self.MODE_MENU:
            self.display.menu_right()
        elif self.mode == self.MODE_CLOCK:
            self.clock.button2()

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

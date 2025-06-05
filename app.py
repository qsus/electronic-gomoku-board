import asyncio
from board import Board
import json
from server import Server
from secret import SSID, PASSWORD, AP_SSID, AP_PASSWORD
from display import Display
from wifi import WifiConnection




class App:
    def __init__(self):
        self.board = Board()
        self.board.calibrate()
        self.wifi_connection = WifiConnection()
        self.display = Display()
        self.server = Server(self.board)

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

    async def main(self):
        # Create tasks to run concurrently
        server_task = asyncio.create_task(self.server.start())
        board_task = asyncio.create_task(self.board.start_monitoring())
        
        # Wait for both tasks indefinitely
        await asyncio.gather(server_task, board_task)

if __name__ == "__main__":
    app = App()
    asyncio.run(app.main())

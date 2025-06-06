# Electronic Gomoku Board
## Useful links
- https://github.com/Bucknalla/micropython-i2c-lcd/
- https://microdot.readthedocs.io/
## App
Firmware for the EGB is based on Raspberry Pi Pico W and written in MicroPython, separated into classes. Few notes about the implementation:
- `main.py` is run automatically unless REPL (read-eval-print loop - a command line interface) is connected.
- `App` is the main class that instantiates all other classes.
- Some classes such as `Clock` use `asyncio` to run some kind of monitoring loop (`asyncio.create_task(self._async_loop())` in `Clock`). Others, such as `Board` or `Server` expose `async` method, which is then run in the `App` class (`asyncio.create_task(self.server.start())` in `App`). This is yet to be refactored, if only I knew which solution is better. 
- (not yet implemented correctly) All files may access `config.py` and `secret.py` to load configuration and wifi credentials. These files can be edited using the web interface. Note that if you download the project from GitHub, you will need to copy `secret.example.py` to `secret.py` and fill in your wifi credentials.

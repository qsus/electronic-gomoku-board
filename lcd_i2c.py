from machine import I2C, Pin
from time import sleep_ms

class I2cLcd:
    def __init__(self, i2c, addr, rows=2, cols=16):
        self.i2c = i2c
        self.addr = addr
        self.rows = rows
        self.cols = cols
        self.backlight = 0x08
        self._init_lcd()

    def _write(self, data):
        self.i2c.writeto(self.addr, bytearray([data | self.backlight]))

    def _pulse(self, data):
        self._write(data | 0x04)  # Enable bit high
        sleep_ms(1)
        self._write(data & ~0x04)  # Enable bit low
        sleep_ms(1)

    def _send(self, data, mode):
        high = mode | (data & 0xF0)
        low = mode | ((data << 4) & 0xF0)
        self._pulse(high)
        self._pulse(low)

    def _cmd(self, cmd):
        self._send(cmd, 0)

    def _char(self, char):
        self._send(ord(char), 0x01)

    def _init_lcd(self):
        sleep_ms(50)
        self._pulse(0x30)
        sleep_ms(5)
        self._pulse(0x30)
        sleep_ms(1)
        self._pulse(0x30)
        self._pulse(0x20)
        self._cmd(0x28)  # 4-bit, 2 lines
        self._cmd(0x0C)  # Display on, no cursor
        self._cmd(0x06)  # Entry mode
        self.clear()

    def clear(self):
        self._cmd(0x01)
        sleep_ms(2)

    def move_to(self, col, row):
        addr = 0x80 + (0x40 * row + col)
        self._cmd(addr)

    def putstr(self, string):
        for c in string:
            self._char(c)

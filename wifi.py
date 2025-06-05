from secret import SSID, PASSWORD, AP_SSID, AP_PASSWORD
import network
from config import PREFER_CLIENT

class WifiConnection:
	def __init__(self):
		if PREFER_CLIENT:
			self.set_client()
		else:
			self.set_ap()

	def set_client(self):
		self.wifi = network.WLAN(network.STA_IF)
		self.wifi.active(True)
		self.wifi.config(pm=0) # disable power saving - it would introduce delays in seconds
		self.wifi.connect(SSID, PASSWORD)
		self.wifi.deinit()

	def set_ap(self):
		self.wifi = network.WLAN(network.AP_IF)
		self.wifi.active(True)
		self.wifi.config(essid=AP_SSID, password=AP_PASSWORD, pm=0)

	def disable(self):
		self.wifi.disconnect()
		self.wifi.deinit()

	def get_ip(self):
		if self.wifi.active():
			return self.wifi.ifconfig()[0]
		return None

	def get_ap_credentials(self):
		if self.wifi.IF_AP:
			return self.wifi.config('essid'), self.wifi.config('password')
		return None, None

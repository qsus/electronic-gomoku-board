def wifiConnect(ssid = '', password = ''):
	import network
	import time

	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	wlan.config(pm = 0) # disable power saving - it would introduce delays in seconds

	if not wlan.isconnected():
		print('Connecting to network...')
		wlan.connect(ssid, password)

		while not wlan.isconnected():
			time.sleep(1)

	print('Network config:', wlan.ifconfig())

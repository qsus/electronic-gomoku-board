from microdot import Microdot, send_file, Request, websocket
from microdot.websocket import with_websocket
import asyncio


from main import wifiConnect
wifiConnect()
app = Microdot()


@app.route('/')
async def index(request: Request):
    return send_file('static/index.html', content_type='text/html')

@app.route('/ws')
@with_websocket
async def ws(request, ws):
    while True:
        message = await ws.receive()
        await ws.send(message)

def readPins():
    pass



# run server
async def main():
    print("Starting web server...")
    server = asyncio.create_task(app.start_server(port=80))
    await server

asyncio.run(main())

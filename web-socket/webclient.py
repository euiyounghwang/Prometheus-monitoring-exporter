import asyncio
import websockets
import websocket
import time
import datetime

message = ['test', 'test1', 'test2']

"""
async def hello():
    async with websockets.connect("ws://localhost:9998") as websocket:
        # msg = input("Enter a message to send to the server: ")
        while True:
            msg = 'alert'
            if message:
                for m in message:
                    await websocket.send(str(datetime.datetime.now()) + ":" + m)
                    response = await websocket.recv()
                    print(f"Received from server: {response}")
            time.sleep(1)

asyncio.get_event_loop().run_until_complete(hello())
"""

''' https://github.com/python-websockets/websockets '''
from websockets.sync.client import connect

def hello():
    with connect("ws://localhost:9998") as websocket:
        websocket.send("Hello world!")
        # message = websocket.recv()
        # print(f"Received: {message}")

while True:
    print('tt')
    hello()
    time.sleep(5)
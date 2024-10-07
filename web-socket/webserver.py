import asyncio;
import websockets;
 
"""
async def accept(websocket, path):
  while True:
    data = await websocket.recv();
    print("receive : " + data);
    await websocket.send("echo : " + data);

 
start_server = websockets.serve(echo, "localhost", 9998);
asyncio.get_event_loop().run_until_complete(start_server);
asyncio.get_event_loop().run_forever();
"""

"""
import asyncio
import time
from websockets.server import serve

async def echo(websocket):
    while True:
        # async for message in websocket:
        #     await websocket.send("echo : " + message)
        print('tt')
        await websocket.send("echo : " + 'test')
        # time.sleep(5)

async def main():
    async with serve(echo, "localhost", 9998):
        await asyncio.get_running_loop().create_future()  # run forever

asyncio.run(main())
"""

''' Prometheus export will be one of websocket client to send message to others'''
import websockets
import asyncio

# Server data
PORT = 9998
print("Server listening on Port " + str(PORT))

# A set of connected ws clients
connected = set()

# The main behavior function for this server
async def echo(websocket, path):
    print("A client just connected")
    # Store a copy of the connected client
    connected.add(websocket)
    # Handle incoming messages
    try:
        async for message in websocket:
            print("Received message from client: " + message)
            # Send a response to all connected clients except sender
            for conn in connected:
                if conn != websocket:
                    await conn.send("Someone said: " + message)
    # Handle disconnecting clients 
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
    finally:
        connected.remove(websocket)

# Start the server
start_server = websockets.serve(echo, "localhost", PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
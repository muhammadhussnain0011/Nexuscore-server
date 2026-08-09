import asyncio
import websockets
import json

async def test():
    uri = "wss://nexuscore-server.onrender.com/ws/echo"
    async with websockets.connect(uri) as ws:
        message = {
            "type": "control",
            "session_id": "test123",
            "device_id": "myphone",
            "payload": {"msg": "hello nexuscore"},
            "ts": 1234567890
        }
        await ws.send(json.dumps(message))
        response = await ws.recv()
        print("Server replied:", response)

asyncio.run(test())
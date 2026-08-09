import asyncio
import websockets
import json

async def test():
    uri = "wss://nexuscore-server.onrender.com/ws/phone-overflow"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "type": "control",
            "session_id": "session-overflow-test",
            "device_id": "phone-overflow",
            "payload": {},
            "ts": 1723000000000
        }))
        await asyncio.sleep(1)

        for i in range(100):
            await ws.send(b"\x00" * 10)
        print("Sent 100 chunks rapidly")
        await asyncio.sleep(3)

asyncio.run(test())
import asyncio
import websockets
import json

async def test():
    uri = "wss://nexuscore-server.onrender.com/ws/phone-1"
    async with websockets.connect(uri, open_timeout=60) as ws:
        # Step 1: control message with session_id
        await ws.send(json.dumps({
            "type": "control",
            "session_id": "session-abc",
            "device_id": "phone-1",
            "payload": {},
            "ts": 1723000000000
        }))
        await asyncio.sleep(1)

        # Step 2: send audio chunks
        for i in range(3):
            await ws.send(b"\x00\x01" * 50)
            print(f"Sent audio chunk {i+1}")
            await asyncio.sleep(0.5)

asyncio.run(test())
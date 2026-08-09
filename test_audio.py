# test_audio.py
import asyncio
import websockets

async def test():
    uri = "wss://nexuscore-server.onrender.com/ws/phone-1"
    async with websockets.connect(uri) as ws:
        fake_audio = b"\x00\x01\x02\x03" * 100  # fake binary data
        await ws.send(fake_audio)
        print("Sent fake audio chunk")
        await asyncio.sleep(2)

asyncio.run(test())
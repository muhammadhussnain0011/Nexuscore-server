from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Literal

app = FastAPI()

# ---------- Health Check ----------
@app.get("/health")
async def health():
    return {"status": "ok"}

# ---------- Message Envelope Schema ----------
class Envelope(BaseModel):
    type: Literal["audio", "transcript", "translation", "control"]
    session_id: str
    device_id: str
    payload: dict
    ts: int

# ---------- Echo Endpoint (for testing/team verification) ----------
@app.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await websocket.send_json(data)

# ---------- Device Tracking Endpoint ----------
connected_devices = {}

@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await websocket.accept()
    connected_devices[device_id] = websocket
    print(f"✅ {device_id} connected. Total devices: {len(connected_devices)}")

    try:
        while True:
            message = await websocket.receive()

            if "text" in message:
                import json
                data = json.loads(message["text"])
                print(f"📩 JSON from {device_id}: {data}")

            elif "bytes" in message:
                audio_chunk = message["bytes"]
                print(f"🎵 Audio chunk from {device_id}: {len(audio_chunk)} bytes")

    except WebSocketDisconnect:
        del connected_devices[device_id]
        print(f"❌ {device_id} disconnected. Total devices: {len(connected_devices)}")
        
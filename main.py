from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Literal
import json
import asyncio

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

# ---------- Device Tracking + Session Queues ----------
connected_devices = {}
session_queues: dict[str, asyncio.Queue] = {}
session_tasks: dict[str, asyncio.Task] = {}
device_sessions: dict[str, str] = {}

MAX_QUEUE_SIZE = 50


async def get_or_create_queue(session_id: str) -> asyncio.Queue:
    if session_id not in session_queues:
        queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        session_queues[session_id] = queue
        session_tasks[session_id] = asyncio.create_task(process_session_queue(session_id, queue))
        print(f"🆕 Created queue + worker for session {session_id}")
    return session_queues[session_id]


async def process_session_queue(session_id: str, queue: asyncio.Queue):
    while True:
        device_id, message = await queue.get()
        print(f"⚙️ Processing (session={session_id}) from {device_id}: {message}")
        queue.task_done()


async def safe_enqueue(queue: asyncio.Queue, session_id: str, device_id: str, message):
    """Adds a message to the queue. If the queue is full, drops the oldest
    message to make room for the newest one (prioritizes latest real-time data)."""
    try:
        queue.put_nowait((device_id, message))
    except asyncio.QueueFull:
        try:
            queue.get_nowait()  # drop oldest
            queue.put_nowait((device_id, message))
            print(f"⚠️ Queue full for session {session_id} — dropped oldest message to make room")
        except Exception as e:
            print(f"❌ Failed to enqueue after overflow handling: {e}")


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await websocket.accept()
    connected_devices[device_id] = websocket
    print(f"✅ {device_id} connected. Total devices: {len(connected_devices)}")

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                raise WebSocketDisconnect()

            if "text" in message:
                data = json.loads(message["text"])
                session_id = data.get("session_id", "unknown")
                device_sessions[device_id] = session_id

                queue = await get_or_create_queue(session_id)
                await safe_enqueue(queue, session_id, device_id, data)

            elif "bytes" in message:
                audio_chunk = message["bytes"]
                session_id = device_sessions.get(device_id, "unknown")

                queue = await get_or_create_queue(session_id)
                await safe_enqueue(queue, session_id, device_id, f"[audio {len(audio_chunk)} bytes]")

    except WebSocketDisconnect:
        del connected_devices[device_id]
        print(f"❌ {device_id} disconnected. Total devices: {len(connected_devices)}")
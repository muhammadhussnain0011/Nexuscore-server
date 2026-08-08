from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}
from pydantic import BaseModel
from typing import Literal
class Envelope(BaseModel):
    type: Literal["audio","transcript","translation","control"]
    session_id: str
    device_id: str
    payload: dict
    ts: int
from fastapi import WebSocket
@app.websocket("/ws/echo")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await websocket.send_json(data)

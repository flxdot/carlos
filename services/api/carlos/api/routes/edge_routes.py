"""This module contains the routes used by the carlos edge devices to receive data from
the API."""

__all__ = ["edge_router"]

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

edge_router = APIRouter()


class EdgeConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = EdgeConnectionManager()


@edge_router.websocket("/server")
async def edge_server_websocket(websocket: WebSocket):
    """Handles the connection of the edge server to the API."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

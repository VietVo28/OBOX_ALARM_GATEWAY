from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.websocket.ConnectionManager import connection_manager

router = APIRouter()


@router.websocket("/")
async def websocket_super_admin(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.send_all(data)
            print("data", data)
    except WebSocketDisconnect as e:
        print("e", e)
        connection_manager.disconnect(websocket)


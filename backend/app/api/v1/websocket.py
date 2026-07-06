from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.core.logging import logger
from app.db.mongodb import get_database
from app.dashboard.services import DashboardGateway, DashboardService, WidgetService
from app.infrastructure.websocket.auth import validate_ws_token
from app.infrastructure.websocket.manager import connection_manager
from app.utils.date_utils import utc_now

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    user_id = await validate_ws_token(ws)
    if not user_id:
        await ws.close(code=4001)
        return
    await connection_manager.connect(user_id, ws)
    logger.info("WebSocket connected: user=%s", user_id)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(user_id, ws)
        logger.info("WebSocket disconnected: user=%s", user_id)


@router.websocket("/ws/dashboard")
async def dashboard_ws_endpoint(ws: WebSocket):
    user_id = await validate_ws_token(ws)
    if not user_id:
        await ws.close(code=4001)
        return
    await connection_manager.connect(user_id, ws)
    logger.info("Dashboard WebSocket connected: user=%s", user_id)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(user_id, ws)
        logger.info("Dashboard WebSocket disconnected: user=%s", user_id)


@router.post("/ws/dashboard/subscribe")
async def subscribe_dashboard_ws(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict:
    gateway = DashboardGateway()
    gateway.subscribe_to_events()
    return {"status": "subscribed", "user_id": str(current_user["_id"])}

from fastapi import WebSocket

from app.core.security import decode_access_token


async def validate_ws_token(ws: WebSocket) -> str | None:
    token = ws.query_params.get("token")
    if not token:
        return None
    user_id = decode_access_token(token)
    return user_id

from fastapi import WebSocket

from app.core.security import validate_bearer_token


async def validate_ws_token(ws: WebSocket) -> str | None:
    """Validate a Clerk session token supplied as a websocket query parameter.

    Returns the verified Clerk subject when valid, otherwise ``None``.
    """
    token = ws.query_params.get("token")
    if not token:
        return None
    claims = await validate_bearer_token(token)
    if not claims:
        return None
    return claims.get("sub")
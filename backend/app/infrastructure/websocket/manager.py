from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[user_id].add(ws)

    def disconnect(self, user_id: str, ws: WebSocket) -> None:
        self._connections[user_id].discard(ws)
        if not self._connections[user_id]:
            del self._connections[user_id]

    async def send_to_user(self, user_id: str, message: dict) -> None:
        for ws in self._connections.get(user_id, set()):
            await ws.send_json(message)

    async def broadcast(self, message: dict) -> None:
        for user_sockets in self._connections.values():
            for ws in user_sockets:
                await ws.send_json(message)

    @property
    def active_connections(self) -> int:
        return sum(len(sockets) for sockets in self._connections.values())


connection_manager = ConnectionManager()

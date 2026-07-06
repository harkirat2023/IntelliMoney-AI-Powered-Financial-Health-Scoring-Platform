from collections import defaultdict
from typing import Any, Callable, Coroutine

from app.infrastructure.messaging.events import Event

EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].remove(handler)

    async def publish(self, event: Event) -> None:
        for handler in self._subscribers.get(event.event_type, []):
            try:
                await handler(event)
            except Exception:
                import logging
                logging.getLogger("intellimoney").exception(
                    "Event handler failed for %s", event.event_type,
                )


event_bus = EventBus()

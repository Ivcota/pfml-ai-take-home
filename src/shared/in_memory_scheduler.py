from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class ScheduledItem:
    event_type: str
    payload: dict
    fire_at: datetime


class InMemoryScheduler:
    def __init__(self) -> None:
        self._items: list[ScheduledItem] = []
        self._handlers: dict[str, Callable[[dict], None]] = {}

    def schedule(
        self,
        event_type: str,
        payload: dict,
        fire_at: datetime,
    ) -> None:
        self._items.append(ScheduledItem(event_type=event_type, payload=payload, fire_at=fire_at))

    def on(self, event_type: str, handler: Callable[[dict], None]) -> None:
        self._handlers[event_type] = handler

    def trigger_due(self, as_of: datetime | None = None) -> None:
        now = as_of or datetime.now()
        due = [item for item in self._items if item.fire_at <= now]
        self._items = [item for item in self._items if item.fire_at > now]
        for item in due:
            handler = self._handlers.get(item.event_type)
            if handler:
                handler(item.payload)

    @property
    def pending(self) -> list[ScheduledItem]:
        return list(self._items)

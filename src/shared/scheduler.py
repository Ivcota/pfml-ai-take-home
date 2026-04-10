from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID


class Scheduler(Protocol):
    def schedule(
        self,
        event_type: str,
        payload: dict,
        fire_at: datetime,
    ) -> None: ...

    def trigger_due(self, as_of: datetime | None = None) -> None: ...

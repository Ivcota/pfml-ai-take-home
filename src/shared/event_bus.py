from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from src.shared.domain_event import DomainEvent


class EventBus(Protocol):
    def publish(self, event: DomainEvent) -> None: ...

    def subscribe(
        self, event_type: type[DomainEvent], handler: Callable[[DomainEvent], None]
    ) -> None: ...

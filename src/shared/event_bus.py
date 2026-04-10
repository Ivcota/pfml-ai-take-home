from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypeVar

from src.shared.domain_event import DomainEvent

E = TypeVar("E", bound=DomainEvent)


class EventBus(Protocol):
    def publish(self, event: DomainEvent) -> None: ...

    def subscribe(
        self, event_type: type[E], handler: Callable[[E], None]
    ) -> None: ...

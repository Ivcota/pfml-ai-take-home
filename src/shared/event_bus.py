from __future__ import annotations

from typing import Protocol, Callable, Type

from src.shared.domain_event import DomainEvent


class EventBus(Protocol):
    def publish(self, event: DomainEvent) -> None: ...

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None: ...

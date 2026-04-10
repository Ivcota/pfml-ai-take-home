from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from src.shared.domain_event import DomainEvent


class InMemoryEventBus:
    def __init__(self) -> None:
        self._handlers: dict[
            type[DomainEvent], list[Callable[[DomainEvent], None]]
        ] = defaultdict(list)
        self.published: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)
        for handler in self._handlers.get(type(event), []):
            handler(event)

    def subscribe(
        self, event_type: type[DomainEvent], handler: Callable[[DomainEvent], None]
    ) -> None:
        self._handlers[event_type].append(handler)

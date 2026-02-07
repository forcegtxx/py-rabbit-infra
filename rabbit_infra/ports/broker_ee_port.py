from __future__ import annotations

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
    from asyncio import Task
    from rabbit_infra.types import EventHandler, Payload


class BrokerEEPort(Protocol):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    def on(
        self, 
        event_pattern: str, 
        handler: EventHandler
    ) -> Task[None]:
        ...
    
    def emit(
        self, 
        event_name: str,
        payload: Payload, 
        durable: bool = False
    ) -> Task[None]:
        ...

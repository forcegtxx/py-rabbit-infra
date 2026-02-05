from asyncio import Task
from typing import Any, Callable, Awaitable, Protocol

Handler = Callable[[Any], Awaitable[None]]


class RabbitEEPort(Protocol):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    def on(
        self, 
        event_pattern: str, 
        handler: Handler
    ) -> Task[None]:
        ...
    
    def emit(
        self, 
        event_name: str,
        payload: Any, 
        durable: bool = False
    ) -> Task[None]:
        ...

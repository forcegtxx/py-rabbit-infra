from typing import Awaitable, Dict, Any, Protocol, Callable

Handler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


class RabbitRpcServerPort(Protocol):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def register(
        self,
        *,
        service_name: str,
        method: str,
        handler: Handler
    ) -> None:
        ...
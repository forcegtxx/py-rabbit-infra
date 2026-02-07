from __future__ import annotations

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
    from rabbit_infra.types import RpcHandler


class BrokerRpcServerPort(Protocol):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def register(
        self,
        *,
        service_name: str,
        method: str,
        handler: RpcHandler
    ) -> None:
        ...
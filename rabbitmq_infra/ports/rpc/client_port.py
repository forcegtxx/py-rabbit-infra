from __future__ import annotations

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
    from rabbitmq_infra.types import Payload


class BrokerRpcClientPort(Protocol):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def call(
        self,
        *,
        service_name: str,
        method: str,
        payload: Payload,
        timeout: int = 5
    ) -> Payload:
        ...
from typing import Dict, Any, Protocol


class RabbitRpcClientPort(Protocol):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def call(
        self,
        *,
        service_name: str,
        method: str,
        payload: Dict[str, Any],
        timeout: int = 5
    ) -> Dict[str, Any]:
        ...
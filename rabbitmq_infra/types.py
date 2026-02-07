from typing import Any, Awaitable, Callable, Dict

Payload = Dict[str, Any]

RpcHandler = Callable[[Payload], Awaitable[Payload]]
EventHandler = Callable[[Payload], Awaitable[None]]


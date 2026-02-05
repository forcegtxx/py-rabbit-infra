from typing import Dict, Any, Protocol
from aio_pika.abc import AbstractQueue, AbstractExchange


class RabbitClientPort(Protocol):
    """Порт для брокера сообщений (RabbitMQ, Kafka, ...)."""

    async def connect(self) -> None:
        """Подключиться к брокеру."""
        ...

    async def close(self) -> None:
        """Закрыть соединение."""
        ...

    # ============= Queue =============

    async def create_direct_queue(
        self,
        name: str,
        durable: bool = True
    ) -> AbstractQueue:
        ...

    async def create_temporary_queue(self) -> AbstractQueue:
        ...

    # ============= Exchange =============

    async def create_topic_exchange(
        self,
        name: str,
        durable: bool = True
    ) -> AbstractExchange:
        ...

    async def create_fanout_exchange(
        self,
        name: str,
        durable: bool = True
    ) -> AbstractExchange:
        ...

    # ============= Bind =============

    async def bind_queue_to_fanout(
        self,
        queue: AbstractQueue,
        *,
        exchange_name: str | None = None,
        exchange: AbstractExchange | None = None
    ):
        ...

    async def bind_queue_to_topic(
        self,
        *,
        queue: AbstractQueue,
        exchange_name: str | None = None,
        exchange: AbstractExchange | None = None,
        routing_key: str
    ):
        ...

    # ============= Unbind =============

    async def unbind_queue_from_fanout(
        self,
        queue: AbstractQueue,
        *,
        exchange_name: str | None = None,
        exchange: AbstractExchange | None = None
    ):
        ...

    async def unbind_queue_from_topic(
        self,
        queue: AbstractQueue,
        *,
        exchange_name: str | None = None,
        exchange: AbstractExchange | None = None,
        routing_key: str
    ):
        ...

    # ============= Publish =============

    async def publish(
        self,
        *,
        exchange_name: str = "",
        exchange: AbstractExchange | None = None,
        routing_key: str,
        payload: Dict[str, Any],
        durable: bool = False,
        correlation_id: str | None = None,
        reply_to: str | None = None
    ) -> None:
        ...

    @property
    def topic_exchange(self) -> AbstractExchange:
        """Топиковый exchange."""
        ...

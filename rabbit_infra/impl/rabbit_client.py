from __future__ import annotations

import time
import json
from logging import Logger
from aio_pika import connect_robust, Message, DeliveryMode, ExchangeType
from typing import TYPE_CHECKING, Optional, Dict, Any
if TYPE_CHECKING:
    from aio_pika.abc import AbstractQueue, AbstractExchange, AbstractRobustConnection, AbstractChannel

from rabbit_infra.logging import get_class_logger
from rabbit_infra.ports.broker_client_port import BrokerClientPort
from rabbit_infra.exceptions import ConnectionError


class RabbitClient(BrokerClientPort):
    def __init__(self, url: str, topic_exchange_name: str, logger: Optional[Logger] = None):
        self._url = url
        self._topic_exchange_name: str = topic_exchange_name

        if logger is None:
            self._logger = get_class_logger(self)
        else:
            self._logger = logger.getChild(self.__class__.__name__)

        self._topic_exchange: Optional[AbstractExchange] = None
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[AbstractChannel] = None

    async def connect(self):
        try:
            if self.connection:
                return
            
            if (not self._topic_exchange_name):
                raise RuntimeError("topic_exchange_name missing")

            self._logger.info("Connecting to RabbitMQ...")

            self.connection = await connect_robust(self._url)

            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            self._topic_exchange = await self.create_topic_exchange(
                name=self._topic_exchange_name
            )

            self._logger.info("Connected to RabbitMQ")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to RabbitMQ: {e}")

    async def close(self):
        """Закрыть соединение"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        self._logger.info("Connection to RabbitMQ closed")

    # ============= Queue =============

    async def create_direct_queue(
        self,
        name: str,
        durable: bool = True
    ) -> AbstractQueue:
        if self.channel is None:
            raise ConnectionError("RabbitBroker is not connected. Call connect() first.")

        return await self.channel.declare_queue(
            name=name,
            durable=durable,
            exclusive=False
        )

    async def create_temporary_queue(self) -> AbstractQueue:
        if self.channel is None:
            raise ConnectionError("RabbitBroker is not connected. Call connect() first.")
        
        return await self.channel.declare_queue(
            name="",  # auto-generated
            exclusive=True
        )

    # ============= Exchange =============

    async def create_fanout_exchange(
        self,
        name: str,
        durable: bool = True
    ):
        if self.channel is None:
            raise ConnectionError("RabbitBroker is not connected. Call connect() first.")
        
        return await self.channel.declare_exchange(
            name=name,
            type=ExchangeType.FANOUT,
            durable=durable
        )

    async def create_topic_exchange(
        self,
        name: str,
        durable: bool = True
    ):
        if self.channel is None:
            raise ConnectionError("RabbitBroker is not connected. Call connect() first.")
            
        return await self.channel.declare_exchange(
            name=name,
            type=ExchangeType.TOPIC,
            durable=durable
        )

    # ============= Bind =============

    async def bind_queue_to_fanout(
        self,
        queue: AbstractQueue,
        *,
        exchange_name: str | None = None,
        exchange: AbstractExchange | None = None
    ):
        if self.channel is None:
            raise ConnectionError("RabbitBroker is not connected. Call connect() first.")
        
        if exchange is None:
            if exchange_name is None:
                raise ValueError("Need exchange_name or exchange")
            exchange = await self.channel.get_exchange(exchange_name)
        await queue.bind(exchange, routing_key="")

    async def bind_queue_to_topic(
        self,
        *,
        queue: AbstractQueue,
        routing_key: str,
        exchange_name: str | None = None,
        exchange: AbstractExchange | None = None
    ):
        if self.channel is None:
            raise ConnectionError("RabbitBroker is not connected. Call connect() first.")
            
        if exchange is None:
            if exchange_name is None:
                raise ValueError("Need exchange_name or exchange")
            exchange = await self.channel.get_exchange(exchange_name)
        await queue.bind(exchange, routing_key=routing_key)

    # ============= Unbind =============

    async def unbind_queue_from_fanout(
        self,
        queue: AbstractQueue,
        *,
        exchange_name: str | None = None,
        exchange: AbstractExchange | None = None
    ):
        if self.channel is None:
            raise ConnectionError("RabbitBroker is not connected. Call connect() first.")
        
        if exchange is None:
            if exchange_name is None:
                raise ValueError("Need exchange_name or exchange")
            exchange = await self.channel.get_exchange(exchange_name)
        await queue.unbind(exchange, routing_key="")

    async def unbind_queue_from_topic(
        self,
        queue: AbstractQueue,
        *,
        exchange_name: str | None = None,
        exchange: AbstractExchange | None = None,
        routing_key: str
    ):
        if self.channel is None:
            raise ConnectionError("RabbitBroker is not connected. Call connect() first.")
        
        if exchange is None:
            if exchange_name is None:
                raise ValueError("Need exchange_name or exchange")
            exchange = await self.channel.get_exchange(exchange_name)
        await queue.unbind(exchange, routing_key=routing_key)

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
    ):
        if self.channel is None:
            raise ConnectionError("RabbitBroker is not connected. Call connect() first.")
        
        body = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode()
        delivery_mode = DeliveryMode.PERSISTENT if durable else DeliveryMode.NOT_PERSISTENT

        # Выбираем exchange
        if not exchange and exchange_name:
            exchange = await self.channel.get_exchange(exchange_name)
        elif not exchange:
            exchange = self.channel.default_exchange

        await exchange.publish(
            Message(
                body=body, 
                delivery_mode=delivery_mode,
                correlation_id=correlation_id,
                reply_to=reply_to,
                timestamp=time.time()
            ),
            routing_key=routing_key
        )

    @property
    def topic_exchange(self) -> AbstractExchange:
        if self._topic_exchange is None:
            raise ConnectionError("Exchange not created. Call connect() first.")
        return self._topic_exchange

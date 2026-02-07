from __future__ import annotations

import json
import asyncio
from asyncio import Task
from logging import Logger, getLogger
from typing import TYPE_CHECKING, Optional, Any
if TYPE_CHECKING:
    from aio_pika.abc import AbstractExchange, AbstractIncomingMessage
    from rabbit_infra.types import EventHandler
    from ports.broker_client_port import BrokerClientPort

from rabbit_infra.exceptions import ConsumeError
from rabbit_infra.ports.broker_ee_port import BrokerEEPort


class RabbitEE(BrokerEEPort):
    def __init__(self, broker: BrokerClientPort, logger: Optional[Logger] = None):
        self._broker = broker
        
        if logger is None:
            self._logger = getLogger(__name__)
        else:
            self._logger = logger
        
        self._topic_exchange: Optional[AbstractExchange] = None

    async def start(self):
        self._topic_exchange = self._broker.topic_exchange

    async def stop(self):
        pass

    # ============= API =============
    
    def on(
        self, 
        event_pattern: str, 
        handler: EventHandler
    ) -> Task[None]:
        return asyncio.create_task(self._setup_subscription(event_pattern, handler))

    def emit(
        self, 
        event_name: str,
        payload: Any, 
        durable: bool = False
    ) -> Task[None]:
        return asyncio.create_task(self._broker.publish(
            exchange=self._topic_exchange,
            routing_key=event_name,
            payload=payload,
            durable=durable
        ))

    # ============= internal =============

    async def _setup_subscription(self, pattern: str, handler: EventHandler):
        async def wrapper(message: AbstractIncomingMessage):
                try:
                    payload = json.loads(message.body)
                    
                    await handler(payload)

                    await message.ack()
                except Exception as e:
                    await message.nack(requeue=False)
                    self._logger.error(f"Error processing event pattern {pattern}: {e}")
                    raise ConsumeError(f"Error processing event pattern {pattern}")
        
        queue = await self._broker.create_temporary_queue()
        await self._broker.bind_queue_to_topic(
            queue=queue, 
            exchange=self._topic_exchange, 
            routing_key=pattern
        )
        await queue.consume(wrapper)



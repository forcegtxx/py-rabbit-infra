import json
import asyncio
from asyncio import Task
from logging import Logger, getLogger
from aio_pika.abc import AbstractExchange, AbstractIncomingMessage
from typing import Optional, Callable, Dict, Any, Awaitable

from exceptions import ConsumeError
from ports.rabbit_client_port import RabbitClientPort
from ports.rabbit_ee_port import RabbitEEPort

Handler = Callable[[Dict[str, Any]], Awaitable[None]]


class RabbitEE(RabbitEEPort):
    def __init__(self, broker: RabbitClientPort, logger: Optional[Logger] = None):
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

    # ============= ОСНОВНОЙ API =============
    
    def on(
        self, 
        event_pattern: str, 
        handler: Handler
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

    # ============= ВНУТРЕННЯЯ ЛОГИКА =============

    async def _setup_subscription(self, pattern: str, handler: Handler):
        # Создаём временную очередь
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



import json
from logging import Logger, getLogger
from aio_pika.abc import AbstractExchange, AbstractIncomingMessage
from typing import Optional, Dict
from ports.rabbit_client_port import RabbitClientPort
from ports.rpc.server_port import RabbitRpcServerPort, Handler


class RabbitRpcServer(RabbitRpcServerPort):
    def __init__(self, broker: RabbitClientPort, logger: Optional[Logger] = None):
        self._broker = broker
        
        if logger is None:
            self._logger = getLogger(__name__)
        else:
            self._logger = logger

        self._topic_exchange: Optional[AbstractExchange] = None
        self.handlers: Dict[str, Handler] = {}  # "service.method" -> handler

    async def start(self):
        self._topic_exchange = self._broker.topic_exchange

    async def stop(self):
        pass

    async def register(
        self,
        *,
        service_name: str,
        method: str,
        handler: Handler
    ):
        key = f"{service_name}.{method}"
        if key in self.handlers:
            raise ValueError(f"Handler for {key} already registered")
        
        self.handlers[key] = handler

        # Подписываемся ТОЛЬКО на свой метод
        queue = await self._broker.create_temporary_queue()
        await self._broker.bind_queue_to_topic(
            queue=queue, 
            exchange=self._topic_exchange, 
            routing_key=f"rpc.call.{key}"
        )

        await queue.consume(self._create_handler_wrapper(handler))
    
    def _create_handler_wrapper(self, handler: Handler):
        async def wrapper(message: AbstractIncomingMessage):
            try:
                payload = json.loads(message.body)
                result = await handler(payload)

                reply_to = message.reply_to
                if not reply_to:
                    return

                await self._broker.publish(
                    routing_key=reply_to,
                    correlation_id=message.correlation_id,
                    payload={
                        "result": result
                    }
                )

                await message.ack()
            except Exception as e:
                await message.nack(requeue=False)
                self._logger.error(f"Error in handler {handler.__name__}: {e}")

        return wrapper


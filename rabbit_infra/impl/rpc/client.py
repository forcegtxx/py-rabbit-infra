from __future__ import annotations

import uuid
import asyncio
import json
from logging import Logger, getLogger
from typing import TYPE_CHECKING, Optional, Dict, Any 
if TYPE_CHECKING:
    from asyncio import Future
    from aio_pika.abc import AbstractExchange, AbstractIncomingMessage, AbstractQueue
    from ports.broker_client_port import BrokerClientPort
    from ports.broker_client_port import BrokerClientPort

from ...exceptions import RpcTimeoutError
from ...ports.rpc.client_port import BrokerRpcClientPort


class RabbitRpcClient(BrokerRpcClientPort):
    def __init__(self, broker: BrokerClientPort, logger: Optional[Logger] = None):
        self._broker = broker
        
        if logger is None:
            self._logger = getLogger(__name__)
        else:
            self._logger = logger

        self._topic_exchange: Optional[AbstractExchange] = None
        self.callback_queue: AbstractQueue | None = None
        self._pending: Dict[str, Future[Dict[str, Any]]] = {}  # correlation_id -> Future
    
    async def start(self):
        self._topic_exchange = self._broker.topic_exchange

        self.callback_queue = await self._broker.create_temporary_queue()
        # Subscribe to the callback queue to receive responses
        await self.callback_queue.consume(self._on_response)

    async def stop(self):
        pass

    async def _on_response(self, message: AbstractIncomingMessage):
        try:
            corr_id = message.correlation_id
            if corr_id is None:
                await message.nack(requeue=False)
                return
        
            future = self._pending.pop(corr_id, None)
            if future is None or future.done():
                return
            
            payload = json.loads(message.body)
            
            if "error" in payload:
                future.set_exception(Exception(payload["error"]))
            else:
                future.set_result(payload["result"])
            
            await message.ack()
        except Exception as e:
            await message.nack(requeue=False)
            self._logger.error(f"Error processing RPC response: {e}")

    async def call(
        self,
        *,
        service_name: str,
        method: str,
        payload: Dict[str, Any],
        timeout: int = 5
    ) -> Dict[str, Any]:
        """
        Выполнить RPC-вызов
        
        :param service_name: имя сервиса (например, "market_manager")
        :param method: имя метода (например, "get_balance")
        :param params: параметры вызова
        :param timeout: таймаут в секундах
        """
        if self.callback_queue is None:
            raise RuntimeError("RabbitRpcClient is not started. Call start() first.")

        corr_id = str(uuid.uuid4())
        future = asyncio.get_running_loop().create_future()
        self._pending[corr_id] = future

        # Отправляем запрос
        await self._broker.publish(
            exchange=self._topic_exchange,
            routing_key=f"rpc.call.{service_name}.{method}",
            reply_to=self.callback_queue.name,
            correlation_id=corr_id,
            payload=payload
        )

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(corr_id, None)
            raise RpcTimeoutError(f"RPC timeout for method {method} on {service_name}")
        except Exception as e:
            self._pending.pop(corr_id, None)
            self._logger.error(f"RPC error {service_name}.{method}: {e}")
            raise RuntimeError(f"RPC error: {e}") from e
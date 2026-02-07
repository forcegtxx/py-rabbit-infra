import pytest
import asyncio
from typing import Dict, Any, List
from rabbit_infra.ports.broker_client_port import BrokerClientPort
from rabbit_infra import RabbitEE

@pytest.mark.asyncio
async def test_emit_and_on(broker_client: BrokerClientPort):
    ee = RabbitEE(broker_client)
    await ee.start()

    messages: List[str] = []

    async def handler(payload: Dict[str, Any]):
        messages.append(payload["msg"])

    ee.on("event.test", handler)
    await asyncio.sleep(0.1) # wait a short moment to ensure subscription is set up
    await ee.emit("event.test", {"msg": "hello world"})

    await asyncio.sleep(0.1) # wait a short moment to ensure message delivery
    assert messages == ["hello world"]

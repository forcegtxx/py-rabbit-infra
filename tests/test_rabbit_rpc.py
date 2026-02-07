import pytest
from typing import Dict, Any
from rabbitmq_infra import RabbitRpcServer, RabbitRpcClient
from rabbitmq_infra.ports.broker_client_port import BrokerClientPort

@pytest.mark.asyncio
async def test_rpc_call(broker_client: BrokerClientPort):
    server = RabbitRpcServer(broker_client)
    client = RabbitRpcClient(broker_client)
    await server.start()
    await client.start()

    # register a test handler
    async def add_handler(payload: Dict[str, Any]):
        return payload["a"] + payload["b"]

    await server.register(service_name="math", method="add", handler=add_handler)

    result = await client.call(service_name="math", method="add", payload={"a": 1, "b": 2})
    assert result == 3

    await client.stop()
    await server.stop()

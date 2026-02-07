import pytest
from typing import List
from aio_pika.abc import AbstractQueue, AbstractIncomingMessage
from rabbitmq_infra.ports.broker_client_port import BrokerClientPort

@pytest.mark.asyncio
async def test_create_direct_queue(broker_client: BrokerClientPort):
    queue: AbstractQueue = await broker_client.create_direct_queue("test_queue", durable=False)
    assert queue.name == "test_queue"

@pytest.mark.asyncio
async def test_create_temporary_queue(broker_client: BrokerClientPort):
    queue: AbstractQueue = await broker_client.create_temporary_queue()
    assert queue.name != ""  # auto-generated name

@pytest.mark.asyncio
async def test_publish_and_receive(broker_client: BrokerClientPort):
    queue = await broker_client.create_direct_queue("pubsub_queue", durable=False)
    await broker_client.bind_queue_to_topic(queue=queue, routing_key="", exchange_name="test_exchange")

    messages: List[str] = []

    async def callback(msg: AbstractIncomingMessage):
        payload = msg.body.decode()
        messages.append(payload)
        await msg.ack()

    await queue.consume(callback)

    payload = {"hello": "world"}
    await broker_client.publish(exchange_name="test_exchange", routing_key="", payload=payload)

    # wait a short moment to ensure message delivery
    import asyncio; await asyncio.sleep(0.1)

    assert len(messages) == 1
    assert messages[0] == '{"hello":"world"}'

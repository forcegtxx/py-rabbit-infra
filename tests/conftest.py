import os
import pytest_asyncio
from rabbitmq_infra import RabbitClient
from dotenv import load_dotenv

load_dotenv()

@pytest_asyncio.fixture
async def broker_client():
    url = os.getenv("BROKER_URL", "amqp://guest:guest@localhost/")
    client = RabbitClient(url=url, topic_exchange_name="test_exchange")
    await client.connect()

    yield client
    await client.close()

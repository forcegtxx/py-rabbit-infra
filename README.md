
# Async RabbitMQ Client (Hex Architecture Edition)

Современная асинхронная библиотека для работы с RabbitMQ, построенная по принципам **Hexagonal Architecture (Ports & Adapters)**.  
Цель — предоставить стабильный и расширяемый API вокруг `aio-pika`, без жёсткой привязки к реализации и инфраструктуре.

---

# 🚀 Возможности

- Асинхронная работа с RabbitMQ (publish / consume)
- Чёткое разделение **портов (контрактов)** и **адаптеров (реализаций)**
- Возможность подменять адаптеры (для тестов или других брокеров)
- Строгая типизация через Protocol
- Гарантированная изоляция домена от инфраструктуры
- Лёгкая интеграция в любое приложение, написанное по Clean/Hex архитектуре

---

# 📦 Установка

```bash
pip install async-rabbitmq-client
```

(Название условное — подставь своё.)

---

# 🧱 Архитектурная структура

Проект следует схеме Hex Architecture:

```
mybroker/
    ports/              # Контракты (protocols)
        message_broker_port.py
        consumer_port.py

    adapters/           # Реализации портов
        rabbitmq/
            rabbit_broker.py
            rabbit_consumer.py

    application/        # Сервисы, работающие через порты
        publisher_service.py
        consumer_service.py

    models/             # value-objects, DTO, события и пр.
```

## ⭐ Принцип

- **Порт** = контракт (Protocol)  
- **Адаптер** = реализация порта  
- **Application слой** = использует только порты  
- **Infrastructure слой** = спрятан в adapters  

---

# 🔌 Порты: контракты

Порты — это ядро библиотеки. Они определяют API взаимодействия.

Пример порта отправки сообщений:

```python
class MessageBrokerPort(Protocol):
    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        ...
```

---

# 🧩 Адаптеры: конкретные реализации

Например, адаптер RabbitMQ:

```
adapters/
    rabbitmq/
        rabbit_broker.py   # publish
        rabbit_consumer.py # consume
```

Адаптер реализует порт, но приложение его не видит — только контракт.

---

# 🛠 Использование

## Отправка сообщений

```python
from mybroker.adapters.rabbitmq.rabbit_broker import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost/")

await broker.publish(
    routing_key="payments.created",
    payload={"payment_id": 123, "amount": 500},
)
```

## Инъекция зависимостей

Твой код зависит только от порта:

```python
class PaymentService:
    def __init__(self, broker: MessageBrokerPort):
        self._broker = broker
```

Теперь можно подменять реализацию в тестах или на другой брокер.

---

# 🔄 Подписка и консьюмеры

Адаптеры RabbitMQ предоставляют удобный API:

```python
consumer = RabbitConsumer("amqp://guest:guest@localhost/")
await consumer.consume("events", handler=handle_event)
```

---

# 🧪 Тестирование

Порты позволяют легко тестировать приложение, подменяя реализацию:

```python
class FakeBroker(MessageBrokerPort):
    async def publish(self, routing_key: str, payload: dict):
        self.sent = (routing_key, payload)
```

Полная изоляция от инфраструктуры — то, что и нужно.

---

# 🧭 Почему именно Hex Architecture?

- Никакой зависимости домена от инфраструктуры
- Взаимозаменяемые адаптеры
- Возможность добавить поддержку Kafka/SQS, не меняя API
- Мощная типизация и предсказуемость
- Простое тестирование

---

# 👨‍💻 Roadmap

- [ ] Поддержка retry/backoff
- [ ] Middleware на порт
- [ ] Многопоточное потребление
- [ ] Инструменты мониторинга
- [ ] Пулы каналов/коннекшенов

---

# 📄 Лицензия

MIT (или своя).

---

# 🌟 Обратная связь

Если хочешь развить библиотеку дальше — открывай issue или PR!  
Или просто напиши автору — идеи приветствуются.

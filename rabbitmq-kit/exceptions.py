class RabbitKitError(Exception):
    """Базовое исключение библиотеки RabbitMQ Kit"""

class ConnectionError(RabbitKitError):
    """Ошибка подключения к брокеру RabbitMQ"""

class QueueError(RabbitKitError):
    """Ошибка создания или доступа к очереди"""

class ExchangeError(RabbitKitError):
    """Ошибка создания или доступа к exchange"""

class PublishError(RabbitKitError):
    """Ошибка при отправке сообщения"""

class ConsumeError(RabbitKitError):
    """Ошибка при обработке входящего сообщения"""

class RpcTimeoutError(RabbitKitError):
    """RPC вызов превысил таймаут"""

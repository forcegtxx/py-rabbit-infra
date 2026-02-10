import logging

LIBRARY_NAME = "rabbit_infra"


def get_library_logger() -> logging.Logger:
    """
    Return the root logger for the library.
    Users can configure this externally.
    """
    return logging.getLogger(LIBRARY_NAME)


def get_logger(name: str) -> logging.Logger:
    """
    Internal helper for modules inside the library.
    Returns hierarchical loggers:
    rabbit_infra.client
    rabbit_infra.ee
    """
    return logging.getLogger(f"{LIBRARY_NAME}.{name}")


def get_class_logger(obj) -> logging.Logger:
    """
    Logger for a specific class.
    rabbit_infra.client.RabbitClient
    """
    module = obj.__class__.__module__.split(".", 1)[-1]
    class_name = obj.__class__.__name__
    return logging.getLogger(f"{LIBRARY_NAME}.{module}.{class_name}")

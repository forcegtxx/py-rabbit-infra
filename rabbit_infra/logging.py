import logging

PROJECT_NAME = "rabbit_infra"

logger: logging.Logger = logging.getLogger(PROJECT_NAME)

def get_logger(name: str | None = None) -> logging.Logger:
    if not name:
        return logger
    return logger.getChild(name)
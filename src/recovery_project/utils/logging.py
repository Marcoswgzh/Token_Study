#class written by Giorgio Di Rosa
"""Logging setup for the recovery project."""

import logging

_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
_CONFIGURED: set[str] = set()


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger with a console handler. Idempotent per *name*."""
    logger = logging.getLogger(name)

    if name not in _CONFIGURED:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_FORMAT))
        logger.addHandler(handler)
        _CONFIGURED.add(name)

    return logger

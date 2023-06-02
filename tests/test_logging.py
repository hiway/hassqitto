from hassquitto import logging
from logging import StreamHandler
from logging import NOTSET
from logging import Formatter
from logging import Logger


def test_get_logger():
    logger = logging.get_logger("test_logger")
    assert isinstance(logger, Logger)
    assert logger.name == "test_logger"
    assert logger.level == NOTSET
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], StreamHandler)
    assert isinstance(logger.handlers[0].formatter, Formatter)

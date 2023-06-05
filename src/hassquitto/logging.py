"""
Logging
"""
import logging as _logging


def get_logger(name: str) -> _logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: Name of the logger.

    Returns:
        Logger.

    Logging to stdout is disabled by default.
    To enable logging, set the level.

        import logging
        logging.getLogger("hassquitto").setLevel(logging.DEBUG)
    """
    logger = _logging.getLogger(name)
    formatter = _logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
    handler = _logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(_logging.NOTSET)
    return logger

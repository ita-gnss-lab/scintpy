"""`scint` package docstring."""  # TODOC:

import sys

from loguru import logger

from . import geom

__all__ = ["geom"]


def _setup_logging() -> None:
    # remove default logger config
    logger.remove()
    # set up file logging
    # TRACE
    logger.add(
        "logs/trace.log",
        level="TRACE",
        rotation="1 day",
        retention="5 days",
        filter=lambda record: record["level"].name == "TRACE",
    )
    # DEBUG
    logger.add(
        "logs/debug.log",
        level="DEBUG",
        rotation="1 day",
        retention="5 days",
        filter=lambda record: record["level"].name == "DEBUG",
    )
    # INFO
    logger.add(
        "logs/info.log",
        level="INFO",
        rotation="1 day",
        retention="5 days",
        filter=lambda record: record["level"].name == "INFO",
    )
    # set up CLI logging
    logger.add(
        sys.stdout,
        level="DEBUG",  # NOTE: choose between "TRACE" "DEBUG" "INFO" "CLI"
    )


_setup_logging()

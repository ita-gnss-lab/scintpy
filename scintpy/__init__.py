"""`scint` package docstring."""  # TODOC:

import sys
from typing import Literal

from loguru import logger

from . import geom

__all__ = ["geom"]


def setup_log(level: Literal["TRACE", "DEBUG", "INFO", "CLI"] = "INFO") -> None:
    """Set up the STDOUT log configuration.

    By default, `scintpy` sets up the STDOUT log level for INFO or above. This default
    setting can be overwritten by the enduser.

    Parameters
    ----------
    level : Literal["TRACE", "DEBUG", "INFO", "CLI"], optional
        The STDOUT log level, by default "INFO".
    """
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
        level=level,
    )


setup_log()

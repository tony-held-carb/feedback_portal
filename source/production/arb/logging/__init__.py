"""
Internal logging implementation for the ARB portal.

This module contains the actual implementation of the logging functionality.
The public interface is maintained in __get_logger.py to preserve import order.
"""

import logging
import pprint
import sys
from logging import Logger
from pathlib import Path
from typing import Any, Callable


def get_logger(
    file_stem: str | None = "app_logger",
    file_path: str | Path | None = None,
    log_to_console: bool = False,
    level: int = logging.DEBUG
) -> tuple[Logger, Callable]:
    """
    Return a configured logger instance and a structured logging helper.

    Args:
        file_stem (str | None): Name used for the logger and log filename (e.g., "xl_create", "arb_portal").
        file_path (str | Path | None): Directory path to store logs. If None, uses "logs/" subdirectory in current working directory.
        log_to_console (bool): Whether to also output logs to the console.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO). Defaults to logging.DEBUG.

    Returns:
        tuple[Logger, Callable]: A configured logger and a pretty-print function.
    """
    log_format = "+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-16s | user:anonymous | %(lineno)-5d | %(filename)-20s | %(message)s"
    log_datefmt = "%Y-%m-%d %H:%M:%S"

    # Sanitize the file_stem for use as filename
    if file_stem:
        file_stem = file_stem.replace(".", "_")
    else:
        file_stem = "app_logger"

    # Determine log directory
    if file_path is None:
        file_path = Path.cwd() / "logs"
    else:
        file_path = Path(file_path)

    # Create log file path
    log_file = file_path / f"{file_stem}.log"

    # Create or retrieve logger
    logger = logging.getLogger(file_stem)

    # Only log configuration message the first time
    if not logger.handlers:
        file_path.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))
        logger.addHandler(file_handler)
        logger.setLevel(level)
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))
            logger.addHandler(console_handler)
        logger.debug(f"Logger '{file_stem}' configured. Log file: {log_file} (level={logging.getLevelName(level)})")
    # No else: do not log anything for subsequent calls

    _, pp_log = get_pretty_printer()
    return logger, pp_log


def get_pretty_printer(**kwargs: Any) -> tuple[pprint.PrettyPrinter, Callable]:
  """
  Return a `PrettyPrinter` instance and a formatting function for structured logging.

  This is useful for debugging or logging nested data structures like dictionaries
  or deeply nested lists.

  Args:
    **kwargs (Any): Options passed to `pprint.PrettyPrinter`, including:
      - indent (int): Indentation level (default: 4).
      - sort_dicts (bool): Whether to sort dictionary keys (default: False).
      - width (int): Max character width per line (default: 120).

  Returns:
    tuple[PrettyPrinter, callable]: Printer object and its .pformat method.
  """
  options = {
    "indent": 4,
    "sort_dicts": False,
    "width": 120
  }
  options.update(kwargs)

  pp = pprint.PrettyPrinter(**options)
  return pp, pp.pformat


if __name__ == "__main__":
  logger, pp_log = get_logger("test_logger", log_to_console=True)
  logger.debug(f"Hello, world!")
  logger.debug(pp_log({"hello": "world"}))
  logger.debug(pp_log({"hello": "world", "nested": {"data": "structure"}})) 
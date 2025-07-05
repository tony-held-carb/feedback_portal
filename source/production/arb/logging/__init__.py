"""
Internal logging implementation for the ARB portal.

This module contains the actual implementation of the logging functionality.
The public interface is maintained in __get_logger.py to preserve import order.
"""

import logging
import pprint
import sys
import inspect
from logging import Logger
from pathlib import Path
from typing import Any, Callable


def get_logger(
    logger_name: str | None = None,
    log_dir: str | Path | None = None,
    log_to_console: bool = False,
    level: int = logging.DEBUG
) -> tuple[Logger, Callable]:
    """
    Return a configured logger instance and a structured logging helper.

    Args:
        logger_name (str | None): Name used for the logger and log filename. If None, uses the caller's module name. If '__main__' or '__init__', uses the script filename or 'app_logger'.
        log_dir (str | Path | None): Directory path to store logs. If None, uses "logs/" subdirectory in current working directory.
        log_to_console (bool): Whether to also output logs to the console.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO). Defaults to logging.DEBUG.

    Returns:
        tuple[Logger, Callable]: A configured logger and a pretty-print function.

    Examples:
        # Basic usage - uses module name automatically
        logger, pp_log = get_logger()
        
        # Named logger with custom directory
        logger, pp_log = get_logger("my_script", log_dir="/var/logs")
        
        # Script with console output and INFO level
        logger, pp_log = get_logger("xl_create", log_to_console=True, level=logging.INFO)
        
        # Portal app with project root logging
        logger, pp_log = get_logger("arb_portal", log_dir=Path(__file__).parents[3] / "logs")
    """
    log_format = "+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-16s | user:anonymous | %(lineno)-5d | %(filename)-20s | %(message)s"
    log_datefmt = "%Y-%m-%d %H:%M:%S"

    # Determine logger_name if not provided
    if logger_name is None:
        logger_name = _get_default_logger_name()

    # Sanitize the logger_name for use as filename
    if logger_name:
        logger_name = str(logger_name).replace(".", "_")
    else:
        logger_name = "app_logger"

    # Determine log directory
    if log_dir is None:
        log_dir = Path.cwd() / "logs"
    else:
        log_dir = Path(log_dir)

    # Create log file path
    log_file = log_dir / f"{logger_name}.log"

    # Create or retrieve logger
    logger = logging.getLogger(logger_name)

    # Track if this is the very first logger configuration in the process
    _first_logger_setup = not hasattr(get_logger, '_first_setup_done')
    
    # Only log configuration message the first time
    if not logger.handlers:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))
        logger.addHandler(file_handler)
        logger.setLevel(level)
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))
            logger.addHandler(console_handler)
        
        # Print diagnostic information only on the very first logger setup
        if _first_logger_setup:
            print(f"🔧 Logger '{logger_name}' configured:")
            print(f"   📁 Log file: {log_file}")
            print(f"   📂 Log directory: {log_dir}")
            print(f"   📊 Level: {logging.getLevelName(level)}")
            print(f"   🖥️ Console output: {'Yes' if log_to_console else 'No'}")
            print()
            get_logger._first_setup_done = True
        
        logger.debug(f"Logger '{logger_name}' configured. Log file: {log_file} (level={logging.getLevelName(level)})")
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

def _get_default_logger_name() -> str:
    """
    Determine a default logger name based on the caller's module or script.

    Returns:
        str: The logger name. Uses the caller's module name if available.
        - If called from a module, returns the module's name (e.g., 'arb.utils.excel').
        - If called from a script (__main__), returns the script filename (without extension).
        - If called from __init__, returns the script filename or 'app_logger'.
        - Falls back to 'app_logger' if context cannot be determined.
    """
    frame = inspect.currentframe()
    if frame is not None and frame.f_back is not None:
        caller = frame.f_back
        logger_name = caller.f_globals.get('__name__', 'app_logger')
        if logger_name in ("__main__", "__init__"):
            script_file = caller.f_globals.get('__file__')
            if script_file:
                return Path(script_file).stem
            else:
                return "app_logger"
        return logger_name
    return "app_logger"


if __name__ == "__main__":
  logger, pp_log = get_logger("test_logger", log_to_console=True)
  logger.debug(f"Hello, world!")
  logger.debug(pp_log({"hello": "world"}))
  logger.debug(pp_log({"hello": "world", "nested": {"data": "structure"}})) 
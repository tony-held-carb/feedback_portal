"""
Centralized logging utility for use across the ARB portal (or any Python project).

This module should be imported first in any file that requires logging. It is
deliberately named `__get_logger.py` to ensure that it appears first when imports
are sorted alphabetically—ensuring logging is configured before any modules emit log messages.

Key Features:
-------------
- Initializes logging once per Python process to prevent redundant configurations.
- Automatically creates log files under a `logs/` directory, named after the entry-point script
  (e.g., running `wsgi.py` results in `logs/wsgi.log`).
- Provides a built-in `PrettyPrinter` helper for human-readable, structured log output.
- Supports console logging (optional) and custom output paths for log files.

Usage Examples:
---------------
Import and initialize the logger in any module:

    from arb import __get_logger as get_logger
    logger, pp_log = get_logger(__name__)

    logger.debug("Basic log message")
    logger.debug(pp_log({"structured": "data", "for": "inspection"}))

To customize behavior:

    logger, pp_log = get_logger(
      file_stem=__name__,
      log_to_console=True,
      force_command_line=False,
      file_path="custom_logs/"
    )

Configuration Behavior:
-----------------------
- If `file_path` is provided, logs are written to that directory using the provided `file_stem`.
- If `file_path` is not provided, the logger writes to `logs/<stem>.log`.
- If executed from `__main__` or `__init__`, the log file defaults to `logs/app_logger.log`.
- All log files use UTF-8 encoding and include timestamps with millisecond precision.

Recommendation:
---------------
Place `__get_logger.py` near the root of your source tree and import it as early
as possible in each module to guarantee consistent logging setup.

This ensures predictable, centralized logging behavior across your entire project.
"""

import logging
import pprint
import sys
from logging import Logger
from pathlib import Path


def get_logger(
    file_stem: str | None = "app_logger",
    file_path: str | Path | None = None,
    log_to_console: bool = False,
    force_command_line: bool = False
) -> tuple[Logger, any]:
  """
  Return a configured logger for a module with an optional pretty-print helper.

  This function configures the logger only once per process. Log messages
  are written to a file (default: logs/<stem>.log) and optionally echoed
  to the console. A pretty-print function is returned for structured logging.

  Args:
    file_stem (str): The stem name for the logger and log file.
    file_path (str | Path | None): Optional path to the log directory (default: logs/).
    log_to_console (bool): Whether to stream log output to the console.
    force_command_line (bool): If True, use the script name as the log file stem.

  Returns:
    tuple:
      - logging.Logger: Configured logger instance.
      - (object) -> str: Pretty-print formatter for structured logs.

  Examples:
    >>> logger, pp_log = get_logger("my_module")
    >>> logger.info(pp_log({"status": "success"}))

  Notes:
    - Log file path defaults to logs/<file_stem>.log
    - If logger is started from `__main__`, the stem defaults to 'app_logger'
    - Logging configuration is skipped if already initialized
  """
  # log_format_old = "+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(filename)s | %(lineno)d | %(message)s"
  log_format_proposed = "+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(filename)s | %(lineno)d | user:%(user)s | %(message)s"
  log_format = "+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-16s | user:anonymous | %(lineno)-5d | %(filename)-20s | %(message)s"
  log_datefmt = "%Y-%m-%d %H:%M:%S"

  # Determine file stem based on command-line script if requested
  if force_command_line:
    script_path = Path(sys.argv[0])
    file_stem = script_path.stem

  if file_stem in [None, "", "__init__", "__main__"]:
    file_stem = "app_logger"

  file_stem = file_stem.replace(".", "_")

  # Default to logs/ directory next to this file
  if file_path is None:
    file_path = Path(__file__).parent / "logs"
  else:
    file_path = Path(file_path)

  file_name = file_path / f"{file_stem}.log"

  # Create or retrieve logger
  logger = logging.getLogger(file_stem)
  is_logger_already_configured = bool(logging.getLogger().handlers)

  if not is_logger_already_configured:
    file_name.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
      level=logging.DEBUG,
      format=log_format,
      datefmt=log_datefmt,
      filename=str(file_name),
      encoding="utf-8",
    )

  # Optional console logging (only add if one doesn't already exist)
  if log_to_console:
    root_logger = logging.getLogger()
    has_console_handler = any(
        isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler)
        for handler in root_logger.handlers
    )
    if not has_console_handler:
      console_handler = logging.StreamHandler()
      console_handler.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))
      root_logger.addHandler(console_handler)

  logger.debug(f"get_logger() called with {file_stem = }, {file_path =}, {log_to_console =}, {force_command_line =}, {sys.argv = }")
  if is_logger_already_configured:
    logging.debug("Logging has already been initialized; configuration will not be changed.")
  else:
    logging.debug(f"Logging was initialized on first usage. Outputting logs to {file_name}")

  _, pp_log = get_pretty_printer()
  return logger, pp_log


def get_pretty_printer(**kwargs) -> tuple[pprint.PrettyPrinter, any]:
  """
  Return a `PrettyPrinter` instance and a formatting function for structured logging.

  This is useful for debugging or logging nested data structures like dictionaries
  or deeply nested lists.

  Args:
    **kwargs: Optional arguments for `pprint.PrettyPrinter`. Defaults include:
      - indent (int): Number of spaces per indent level (default: 4)
      - sort_dicts (bool): Whether to sort dictionary keys (default: False)
      - width (int): Maximum output line width (default: 120)

  Returns:
    tuple:
      - pprint.PrettyPrinter: Pretty printer instance.
      - (object) -> str: Function to format structured objects as strings.

  Example:
    >>> _, pp = get_pretty_printer(indent=2)
    >>> logger.debug(pp({"a": [1, 2, 3], "b": {"nested": True}}))
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
  root_logger = file_path = Path(__file__).resolve().parents[3] / "logs"
  logger, pp_log = get_logger(file_path=root_logger, log_to_console=True)
  logger.debug("Hello, world!")
  logger.debug(pp_log({"hello": "world"}))
  logger.debug(pp_log({"hello": "world", "nested": {"data": "structure"}}))

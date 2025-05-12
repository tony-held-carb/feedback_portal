"""
Provides a centralized logging utility for use across any Python project.

This module should be placed at the root of the project and imported as the first module in any
file that requires logging. It is deliberately named `__get_logger.py` to ensure that, when
imports are sorted alphabetically, this module appears first—guaranteeing that logging is
configured before any other modules emit log messages.

Key Features:
-------------
- Initializes logging once per Python process, preventing redundant or conflicting configurations.
- Automatically creates log files under a `logs/` directory, named after the entry-point script
  (e.g., `wsgi.py` results in `logs/wsgi.log`).
- Includes a `PrettyPrinter` shortcut for structured, human-readable log messages.
- Supports optional console logging and custom log file output paths.

Usage Example:
--------------
Import and initialize logging in any module (including `__init__.py`):

    from arb import __get_logger as get_logger
    logger, pp_log = get_logger(__name__)

    logger.debug("Simple log message")
    logger.debug(pp_log({"structured": "data", "for": "inspection"}))

You may also specify options:

    logger, pp_log = get_logger(
        name=__name__,
        log_to_console=True,
        force_command_line=False,
        logger_path="custom_logs/my_script.log"
    )

Configuration Behavior:
-----------------------
- If `logger_path` is provided, all logs are written to that file.
- If not, the log file is named after the CLI entry point (default behavior) or module name.
- If run from an `__init__` or `__main__` context, the log file is named `app_logger.log`.
- All logs are UTF-8 encoded and include millisecond-precision timestamps and source metadata.

Recommendation:
---------------
Place `__get_logger.py` in the root of your source tree and always import it before any
other logging calls. This ensures predictable, consistent logging behavior across all modules.
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
  Returns a configured logger for a module with a pretty-print helper.

  This function initializes logging once per process. By default, it sets the log filename
  based on the script that started the app (e.g., 'wsgi.py' → 'logs/wsgi.log'), unless a
  custom `file_path` is provided.

  Args:
      file_stem (str): Stem of the file (typically from __name__ or Path(__file__).stem).
      file_path (str | Path | None): Optional. Directory for the log file. Defaults to 'logs/' in the current module.
      log_to_console (bool): If True, also outputs logs to the console. Default is False.
      force_command_line (bool): If True, uses the CLI script name for the log filename.
                                 If False (default), uses the provided `file_stem`.

  Returns:
      tuple:
          logger (Logger): The configured logger object.
          pp_log (Callable[[any], str]): A pretty-printing function for structured log output.

  Examples:
      >>> logger, pp_log = get_logger("my_module")
      >>> logger, pp_log = get_logger("my_module", log_to_console=True)
      >>> logger, pp_log = get_logger("my_module", force_command_line=False)
      >>> logger, pp_log = get_logger("my_module", file_path="custom_logs")

  Logging Behavior:
      - Only configures logging if it hasn’t been configured yet.
      - Log filename is derived from the CLI entry point (default) or the module name.
      - All subsequent calls inherit the configured root logger.
      - Logs are written to logs/<name>.log or to the specified directory.
      - If the logger was started from `__main__` or `__init__`, the log filename defaults to 'app_logger.log'.
  """
  log_format = "+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(filename)s | %(lineno)d | %(message)s"
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
  Returns a `PrettyPrinter` object and a function for pretty-printing log messages.

  This is helpful for structured logging of complex Python objects (e.g., dicts, lists).

  Args:
      **kwargs: Keyword arguments passed to `pprint.PrettyPrinter`.
                Default options include:
                  - indent (int): Indentation level for nested structures (default: 4)
                  - sort_dicts (bool): Do not sort dictionary keys (default: False)
                  - width (int): Maximum line width for output (default: 120)

  Returns:
      tuple:
          pprint.PrettyPrinter: The PrettyPrinter instance
          Callable[[any], str]: A shortcut function to format values for logging

  Example:
      >>> _, pp_log = get_pretty_printer(indent=2)
      >>> logger.debug(pp_log({"hello": "world"}))
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

"""
__get_logger.py should be at the root of any project and simplifies logging.

It is named such that it will always be the first arb module if imports are sorted alphabetically.
Alphabetic sorting of imports ensures predictable ordering of logging imports.

Usage:
  In any module (including __init__.py), add:
      from arb import __get_logger as get_logger
      logger, pp_log = get_logger.get_logger(__name__, __file__)

  - Logging is initialized once per process.
  - Log file is named after the entry-point script (e.g., wsgi.py → logs/wsgi.log).
  - Pretty printer utility is included for structured logging.
"""

import logging
import pprint
import sys
from logging import Logger
from pathlib import Path
from typing import Any

__version__ = "2.0.0"


def get_logger(
    name: str,
    file: str,
    log_to_console: bool = False,
    force_command_line: bool = True
) -> tuple[Logger, Any]:
  """
  Returns a configured logger for a module with a pretty-print helper.

  This function initializes logging once per process. By default, it sets the log filename
  based on the script that started the app (e.g., 'wsgi.py' → 'logs/wsgi.log').

  Args:
    name (str): Typically passed as `__name__` from the calling module.
    file (str): Typically passed as `__file__` from the calling module.
    log_to_console (bool): If True, also outputs logs to the console. Default is False.
    force_command_line (bool): If True (default), use the CLI script name for the log filename.
                               If False, log file will be based on the module name.

  Returns:
    tuple:
      - logger (Logger): The configured logger object.
      - pp_log (Callable[[Any], str]): A pretty-printing function for structured log output.

  Examples:
    >>> logger, pp_log = get_logger(__name__, __file__)
    >>> logger, pp_log = get_logger(__name__, __file__, log_to_console=True)
    >>> logger, pp_log = get_logger(__name__, __file__, force_command_line=False)

  Logging Behavior:
    - Only configures logging if it hasn’t been configured yet.
    - Log filename is derived from the CLI entry point (default) or the module name.
    - All subsequent calls inherit the configured root logger.
    - Logs are written to logs/<name>.log and optionally streamed to console.
    - if the logger was started by a command line that did not have arguments, or an __init__ file
      the logger name is changed to app_logger.log to avoid log file names with special characters.
  """
  print(f"in get_logger {name}, {file}, {log_to_console}, {force_command_line}")
  logger = logging.getLogger(name)

  if not logging.getLogger().handlers:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    if force_command_line:
      script_path = Path(sys.argv[0])
      script_name = script_path.stem
    else:
      script_name = name

    print(f"{script_name}")

    if script_name in [None, "", "__init__", "__main__"]:
      script_name = "app_logger"
      print(f"Renaming log file from {name} to {script_name}")

    log_filename = log_dir / f"{script_name.replace('.', '_')}.log"

    logging.basicConfig(
      level=logging.DEBUG,
      format="+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(filename)s | %(lineno)d | %(message)s",
      datefmt="%Y-%m-%d %H:%M:%S",
      filename=str(log_filename),
      encoding="utf-8",
    )

    if log_to_console:
      console_handler = logging.StreamHandler()
      console_handler.setFormatter(logging.Formatter(
        "+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(filename)s | %(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
      ))
      logging.getLogger().addHandler(console_handler)

    logger.debug(f"__get_logger.get_logger() called with {name = }, {file =}, {log_to_console =}, {force_command_line =}")
    logging.debug(f"Logging was initialized on first usage.  Outputting logs to {log_filename}")
    logging.debug(f"Note: {sys.argv = }")

  else:
    logger.debug(f"__get_logger.get_logger() called with {name = }, {file =}, {log_to_console =}, {force_command_line =}")
    logging.debug(f"Logging has already been initialized so there will be no changes to logging file or options.")

  _, pp_log = get_pretty_printer()
  return logger, pp_log


def get_pretty_printer(**kwargs) -> tuple[pprint.PrettyPrinter, Any]:
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
      - pprint.PrettyPrinter: The actual PrettyPrinter instance
      - Callable[[Any], str]: A shortcut function to format values (used in logging)

  Example:
    >>> _, pp_log = get_pretty_printer(indent=2)
    >>> logger.debug(pp_log(my_complex_object))
  """
  options = {
    "indent": 4,
    "sort_dicts": False,
    "width": 120
  }
  options.update(kwargs)

  pp = pprint.PrettyPrinter(**options)
  return pp, pp.pformat

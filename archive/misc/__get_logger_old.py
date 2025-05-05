"""
__get_logger.py should be at the root of any project and simplifies logging.

It is named such that it will always be the first arb module if imports are sorted alphabetically.
Alphabetic sorting of imports ensures predictable ordering of logging imports.

Notes:
  - All other files that use a logger should import this file with
      import arb.__get_logger as get_logger
  - All other files should have the following line as the first non-import:
      logger, pp_log = get_logger.get_logger(__name__, __file__)
  - pp_log is a formated pretty printer object that allows for formatting printing in the form:
      logger.debug(pp_log(your_object))
"""

import logging
import os
import pprint
from logging import Logger
from pathlib import Path
from typing import Any

__version__ = "1.0.0"


def get_logger(name: str, file: str) -> tuple[Logger, Any]:
  """
  Returns a configured logger for a module with an optional pretty-printing function.

  This function initializes a `logging.Logger` object. If the logger corresponds to
  the main module (`__main__`), it sets up a file-based logging configuration with
  detailed output formatting. Otherwise, the logger inherits from the root logger.
  Additionally, it integrates a pretty-printing utility for structured log messages.

  Args:
      name (str): Name of the logger, typically `__name__`.
      file (str): File name of the logger, typically `__file__`.

  Returns:
      tuple: A tuple containing:
          - `logger` (logging.Logger): The configured logger instance.
          - `pp_log` (callable): A pretty-print function for formatting complex objects
            in log messages.

  Examples:
      >>> logger, pp_log = get_logger(__name__, __file__)
      >>> data = {"key": "value", "another_key": [1, 2, 3]}
      >>> logger.info(pp_log(data))

      If the logger is used in the main module:
      - Logs will be saved in the `logs` directory with a filename based on the module name.

  Logging Configuration (if `name` is `__main__`):
      - Logs are saved in a file named `<module_name>.log` in the `logs` directory.
      - Log format: `+<timestamp> | <level> | <logger_name> | <file_name> | <line_number> | <message>`
      - Example log entry:
        +2025-01-03 12:34:56.789 | DEBUG    | __main__ | example.py | 42 | Sample debug message
  """
  logger = logging.getLogger(name)

  # Check if the module is the main module
  if name == "__main__":
    # Create a logs directory if needed
    dir_path = Path("logs")
    dir_path.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
      filename=f"logs/{os.path.basename(file)[:-3]}.log",  # -3 removes the .py extension
      encoding="utf-8",
      level=logging.DEBUG,
      format="+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(filename)s | %(lineno)d | %(message)s",
      datefmt="%Y-%m-%d %H:%M:%S",
    )

  logger.debug(f"Logger created with name: {name}, file: {file}")
  _, pp_log = get_pretty_printer()

  return logger, pp_log


def get_pretty_printer(**kwargs):
  """
  Returns a `PrettyPrinter` object and a formatted string function for pretty-printing objects
  suitable for logging.

  This function initializes a `PrettyPrinter` instance with customizable options for indentation,
  dictionary sorting, and width. The returned tuple includes the `PrettyPrinter` instance and
  its `pformat` method for logging or outputting pretty-printed strings.

  Args:
      **kwargs: Arbitrary keyword arguments to override default options for the `PrettyPrinter`.
          - `indent` (int): The number of spaces for indentation. Default is 4.
          - `sort_dicts` (bool): Whether to sort dictionary keys. Default is False.
          - `width` (int): The maximum line width for pretty-printed output. Default is 120.

  Returns:
      tuple: A tuple containing:
          - `PrettyPrinter` (pprint.PrettyPrinter): The initialized `PrettyPrinter` object.
          - `pformat` (callable): The `pformat` method of the `PrettyPrinter`, which returns
            a pretty-printed string representation of an object.

  Examples:
      - pp, pp_log = get_pretty_printer(indent=2, width=80)
      -
      - logging.debug(pp_log(your_object))  <-- pretty-printed to logger
  """
  options = {"indent": 4,
             "sort_dicts": False,
             "width": 120}
  options.update(kwargs)
  pp = pprint.PrettyPrinter(**options)
  pp_log = pp.pformat
  return pp, pp_log

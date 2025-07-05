"""
Python Logging Best Practices for ARB Portal
============================================

Key Concepts
------------
- `logging.getLogger(__name__)` returns a logger object for each module, but does NOT create a new log file or handler. All loggers propagate messages to the root logger unless you add handlers to them explicitly.
- Only a call to `logging.basicConfig(...)` or explicit handler setup creates log files or configures output. The first such call in a process sets up the global logging configuration.
- Log messages emitted before `basicConfig` (or handler setup) are sent to a default handler (stderr) or are ignored, depending on severity and environment.
- After `basicConfig`, all loggers (including those created earlier) use the configured handlers (e.g., file, console) for output.
- Multiple calls to `getLogger(__name__)` in different files give you different logger objects (with different names), but unless you add handlers, all messages go to the same global output.
- This design allows you to filter or format logs by module, but keeps log file management centralized and predictable.

Usage Patterns
--------------

1. Web app entry point (e.g., wsgi.py):
  ------------------------------------
    import logging
    from arb_logging import setup_app_logging

    setup_app_logging("arb_portal")

    from arb.portal.app import create_app
    app = create_app()

2. Scripts (e.g., xl_create.py):
  -----------------------------
    import logging
    from arb_logging import setup_standalone_logging

    if __name__ == "__main__":
      setup_standalone_logging("xl_create")

    logger = logging.getLogger(__name__)

3. All other files (including __init__.py):
  ----------------------------------------
    import logging
    from arb_logging import get_pretty_printer

    logger = logging.getLogger(__name__)
    _, pp_log = get_pretty_printer()

    # Usage examples:
    logger.debug("Basic log message")
    logger.info(pp_log({"structured": "data", "for": "inspection"}))

4. Pretty-printing complex objects in logs:
  ----------------------------------------
  The `get_pretty_printer()` function provides a consistent way to format complex data structures in logs:

    from arb_logging import get_pretty_printer
    _, pp_log = get_pretty_printer()
    
    data = {"foo": [1, 2, 3], "bar": {"baz": "qux"}}
    logger.info(pp_log(data))
    
    # Output in log:
    # {
    #   'foo': [1, 2, 3],
    #   'bar': {'baz': 'qux'}
    # }

Implementation
--------------
"""
import logging
import os
from pathlib import Path
from arb.utils.file_io import get_project_root_dir
import pprint
from typing import Callable

APP_DIR_STRUCTURE = ['feedback_portal', 'source', 'production', 'arb', 'portal']

DEFAULT_LOG_FORMAT = "+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-16s | user:anonymous | %(lineno)-5d | %(filename)-20s | %(message)s"
DEFAULT_LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"

def _resolve_log_dir(log_dir: str | Path = "logs", app_dir_structure=None) -> Path:
  """
  Resolve the log directory relative to the project root using directory structure.
  Ensures the directory exists.

  Args:
    log_dir (str | Path): Directory for log files (relative to project root).
    app_dir_structure (list[str] | None): Directory structure to identify project root.
      Defaults to ['feedback_portal', 'source', 'production', 'arb', 'portal'].
  Returns:
    Path: The resolved log directory path.
  """
  if app_dir_structure is None:
    app_dir_structure = APP_DIR_STRUCTURE
  project_root = get_project_root_dir(__file__, app_dir_structure)
  resolved = project_root / log_dir
  resolved.mkdir(parents=True, exist_ok=True)
  return resolved


def setup_standalone_logging(
  log_name: str,
  log_dir: str | Path = "logs",
  level: int = logging.DEBUG,
  app_dir_structure=None,
  log_format: str = DEFAULT_LOG_FORMAT,
  log_datefmt: str = DEFAULT_LOG_DATEFMT
):
  """
  Configure logging for a standalone script. Should be called in the `if __name__ == "__main__"` block.
  Args:
    log_name (str): Name of the log file (without extension).
    log_dir (str | Path): Directory for log files (relative to project root).
    level (int): Logging level (default: DEBUG).
    app_dir_structure (list[str] | None): Directory structure to identify project root.
    log_format (str): Log message format string. Defaults to ARB portal format.
    log_datefmt (str): Log date format string. Defaults to ARB portal format.
  """
  resolved_dir = _resolve_log_dir(log_dir, app_dir_structure)
  logging.basicConfig(
    filename=str(resolved_dir / f"{log_name}.log"),
    level=level,
    format=log_format,
    datefmt=log_datefmt
  )
  print(f"[Logging] Standalone logging configured: {resolved_dir / f'{log_name}.log'} (level={logging.getLevelName(level)})")


def setup_app_logging(
  log_name: str,
  log_dir: str | Path = "logs",
  level: int = logging.DEBUG,
  app_dir_structure=None,
  log_format: str = DEFAULT_LOG_FORMAT,
  log_datefmt: str = DEFAULT_LOG_DATEFMT
):
  """
  Configure logging for the main application (e.g., in wsgi.py). Should be called before importing the app.
  Args:
    log_name (str): Name of the log file (without extension).
    log_dir (str | Path): Directory for log files (relative to project root).
    level (int): Logging level (default: DEBUG).
    app_dir_structure (list[str] | None): Directory structure to identify project root.
    log_format (str): Log message format string. Defaults to ARB portal format.
    log_datefmt (str): Log date format string. Defaults to ARB portal format.
  """
  resolved_dir = _resolve_log_dir(log_dir, app_dir_structure)
  logging.basicConfig(
    filename=str(resolved_dir / f"{log_name}.log"),
    level=level,
    format=log_format,
    datefmt=log_datefmt
  )
  print(f"[Logging] App logging configured: {resolved_dir / f'{log_name}.log'} (level={logging.getLevelName(level)})")


def get_pretty_printer(**kwargs) -> tuple[pprint.PrettyPrinter, Callable[[object], str]]:
  """
  Return a PrettyPrinter instance and a formatting function for structured logging.

  Only import and use this in files where you want to pretty-print complex data structures in your logs.

  Args:
    **kwargs: Options passed to pprint.PrettyPrinter (indent, sort_dicts, width, etc.)
  Returns:
    tuple: (PrettyPrinter instance, .pformat method)

  Examples:
    # Basic usage:
    from arb_logging import get_pretty_printer
    _, pp_log = get_pretty_printer()
    data = {"foo": [1, 2, 3], "bar": {"baz": "qux"}}
    logger.info(pp_log(data))
    # Output in log:
    # {
    #   'foo': [1, 2, 3],
    #   'bar': {'baz': 'qux'}
    # }

    # Custom formatting:
    from arb_logging import get_pretty_printer
    _, pp_log = get_pretty_printer(indent=2, width=80)
    logger.info(pp_log(data))
  """
  options = {
    "indent": 4,
    "sort_dicts": False,
    "width": 120
  }
  options.update(kwargs)
  pp = pprint.PrettyPrinter(**options)
  return pp, pp.pformat 
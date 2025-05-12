"""
Utilities for logging function parameters at runtime.

This module provides tools to assist with debugging and observability by capturing and logging
function names along with the values of all parameters passed to them. It includes:

1. `log_function_parameters`: A standalone function that logs the name and parameters of
   the function in which it is called. Useful for one-off or conditional logging.

2. `log_parameters`: A decorator that automatically logs parameter values each time a
   decorated function is invoked. Useful for consistent logging across multiple functions.

Key Features:
-------------
- Logs in a single-line format: `function_name(param1=val1, param2=val2, ...)`.
- Supports `*args` and `**kwargs`.
- Optionally prints to the console as well as logging to a logger.
- Automatically infers the appropriate logger from the calling module if none is provided.

Example Usage:
--------------
>>> import arb.utils.log_util as log_util
>>> logging.basicConfig(level=logging.DEBUG)

>>> @log_parameters(print_to_console=True)
>>> def greet(name, lang="en"):
>>>     return f"Hello {name} [{lang}]"

>>> def example():
>>>     log_function_parameters(print_to_console=True)

>>> greet("Alice", lang="fr")
>>> example()

Output:
-------
greet(name='Alice', lang='fr')
example()

Recommendations:
----------------
- Use `log_parameters` for consistent tracing of function calls across modules.
- Use `log_function_parameters` for temporary instrumentation or detailed inline debugging.

This module is safe to import in any Python project and requires only the standard library.
"""

import inspect
import logging
from functools import wraps
from typing import Callable

from flask import g, has_request_context


def log_function_parameters(logger: logging.Logger | None = None, print_to_console: bool = False) -> None:
  """
  Logs the calling function's name and all parameters as a single-line message.

  If no logger is provided, one is created using the calling module's `__name__`.

  Args:
      logger (logging.Logger | None): Optional logger to write to. If None, uses logger from caller's module.
      print_to_console (bool): If True, also prints the message to stdout.

  Example:
      >>> log_function_parameters()
      # Logs: my_function(a=1, b=2, kw='yes')
  """
  frame = inspect.currentframe().f_back
  func_name = frame.f_code.co_name

  if logger is None:
    module_name = frame.f_globals.get("__name__", "default_logger")
    logger = logging.getLogger(module_name)

  args_info = inspect.getargvalues(frame)
  params = []

  for arg in args_info.args:
    value = args_info.locals.get(arg)
    params.append(f"{arg}={value!r}")

  if args_info.varargs:
    value = args_info.locals.get(args_info.varargs)
    params.append(f"{args_info.varargs}={value!r}")

  if args_info.keywords:
    kwargs = args_info.locals.get(args_info.keywords, {})
    for k, v in kwargs.items():
      params.append(f"{k}={v!r}")

  log_line = f"{func_name}({', '.join(params)})"
  logger.debug(log_line)
  if print_to_console:
    print(log_line)


def log_parameters(logger: logging.Logger | None = None, print_to_console: bool = False) -> Callable:
  """
  Decorator that logs all arguments passed to a function as a single-line message.

  Args:
      logger (logging.Logger | None): Optional logger to use. If None, uses the logger for the function's module.
      print_to_console (bool): If True, also prints the log line to stdout.

  Returns:
      Callable: A decorated function that logs its parameters on each call.

  Example:
      >>> @log_parameters()
      >>> def greet(name, greeting="Hello"):
      >>>     return f"{greeting}, {name}!"
  """

  def decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
      nonlocal logger
      if logger is None:
        logger = logging.getLogger(func.__module__)
      bound = inspect.signature(func).bind(*args, **kwargs)
      bound.apply_defaults()
      param_str = ", ".join(f"{k}={v!r}" for k, v in bound.arguments.items())
      log_line = f"{func.__name__}({param_str})"
      logger.debug(log_line)
      if print_to_console:
        print(log_line)
      return func(*args, **kwargs)

    return wrapper

  return decorator


class FlaskUserContextFilter(logging.Filter):
  """Injects Flask's g.user into log records."""

  def filter(self, record):
    if has_request_context() and hasattr(g, "user"):
      record.user = g.user
    else:
      record.user = "n/a"
    return True

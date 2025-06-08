"""
log_util.py

Logging utilities to trace function calls and parameter values across the application.

This module provides two main tools for logging function arguments:

    1. log_function_parameters(): Logs the name and arguments of the current function.
    2. log_parameters(): A decorator that logs all arguments of decorated functions.

It also includes a logging filter, FlaskUserContextFilter, to inject the current Flask user
into all log records when inside a request context.

Features:
    - Logs arguments from both positional and keyword inputs.
    - Automatically derives the correct logger based on caller/module context.
    - Supports optional printing to stdout for real-time debugging.
    - Integrates Flask `g.user` context when available, aiding request traceability.

Intended Use:
    - Diagnostic tracing and observability in Flask applications.
    - Debugging individual functions without modifying logic.
    - Enhancing structured logging with contextual request user information.

Dependencies:
    - Python standard library (inspect, logging)
    - Flask (optional, for FlaskUserContextFilter)

Version:
    1.0.0

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


def log_function_parameters(
    logger: logging.Logger | None = None,
    print_to_console: bool = False
) -> None:
  """
  Log the current function's name and arguments using debug-level logging.

  Args:
      logger (logging.Logger | None): Optional logger. If None, derives one from caller's module.
      print_to_console (bool): If True, also prints the message to stdout.

  Example:
      >>> def example(a, b=2): log_function_parameters()
      >>> example(1)
      # Logs: example(a=1, b=2)
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


def log_parameters(
    logger: logging.Logger | None = None,
    print_to_console: bool = False
) -> Callable:
  """
  Decorator to log all arguments passed to a function upon each invocation.

  Args:
      logger (logging.Logger | None): Optional logger instance. Defaults to caller's module logger.
      print_to_console (bool): If True, also prints the log message to stdout.

  Returns:
      Callable: A decorator that logs parameter values each time the function is called.

  Example:
      >>> @log_parameters(print_to_console=True)
      >>> def greet(name, lang="en"):
      >>>     return f"Hello {name} [{lang}]"
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
  """
  Logging filter that injects Flask's `g.user` into log records, if available.

  This allows log formats to include the active Flask user for traceability.

  Adds:
      record.user (str): User identifier from Flask's request context, or "n/a" if unavailable.
  """

  def filter(self, record):
    if has_request_context() and hasattr(g, "user"):
      record.user = g.user
    else:
      record.user = "n/a"
    return True

"""
Python Logging Best Practices for ARB Portal
===========================================

Key Concepts
------------
- `logging.getLogger(__name__)` returns a logger object for each module, but does NOT create a new log file or handler. All loggers propagate messages to the root logger unless you add handlers to them explicitly.
- Only a call to `logging.basicConfig(...)` or explicit handler setup creates log files or configures output. The first such call in a process sets up the global logging configuration.
- Log messages emitted before `basicConfig` (or handler setup) are sent to a default handler (stderr) or are ignored, depending on severity and environment.
- After `basicConfig`, all loggers (including those created earlier) use the configured handlers (e.g., file, console) for output.
- Multiple calls to `getLogger(__name__)` in different files give you different logger objects (with different names), but unless you add handlers, all messages go to the same global output.
- This design allows you to filter or format logs by module, but keeps log file management centralized and predictable.

This module documents and implements a robust, predictable, and flexible logging setup for both
standalone scripts and web applications in the ARB codebase.

Key Points & Recommendations
----------------------------
1. **Configure logging ONCE at the entry point of your application** (e.g., wsgi.py for web apps, or in the `if __name__ == "__main__"` block for scripts).
2. **All other files (including __init__.py) should NOT configure logging**. They should only do:

       import logging
       logger = logging.getLogger(__name__)

3. **Log messages emitted before logging is configured (before basicConfig or handler setup) will go to stderr or be lost.**
   - This is Python's default behavior. It's not an error, but you should be aware of it.
   - For scripts, configure logging as early as possible.
   - For web apps, configure logging at the very top of wsgi.py (before importing the app).
4. **Use a helper function for consistent, DRY setup in scripts.**
5. **Always resolve log file paths relative to the project root, not the current working directory, to avoid log sprawl.**

Flexible Logging Setup Functions
-------------------------------

- `setup_standalone_logging(log_name, log_dir=..., level=...)`: For use in scripts run directly.
- `setup_app_logging(log_name, log_dir=..., level=...)`: For use in wsgi.py or other app entry points.

Usage Patterns
--------------

# For scripts (e.g., xl_create.py):
import logging
from arb_logging import setup_standalone_logging

if __name__ == "__main__":
    setup_standalone_logging("xl_create")

logger = logging.getLogger(__name__)

# For web app entry point (e.g., wsgi.py):
import logging
from arb_logging import setup_app_logging

setup_app_logging("arb_portal")

from arb.portal.app import create_app
app = create_app()

# In all other files (including __init__.py):
import logging
logger = logging.getLogger(__name__)


Implementation
--------------
"""
import logging
import os
from pathlib import Path

def _resolve_log_dir(log_dir: str | Path = "logs") -> Path:
    """
    Resolve the log directory relative to the project root (3 levels up from this file).
    Ensures the directory exists.
    """
    project_root = Path(__file__).resolve().parents[2]  # Adjust as needed for your structure
    resolved = project_root / log_dir
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved

def setup_standalone_logging(log_name: str, log_dir: str | Path = "logs", level: int = logging.DEBUG):
    """
    Configure logging for a standalone script. Should be called in the `if __name__ == "__main__"` block.
    Args:
        log_name (str): Name of the log file (without extension).
        log_dir (str | Path): Directory for log files (relative to project root).
        level (int): Logging level (default: DEBUG).
    """
    resolved_dir = _resolve_log_dir(log_dir)
    logging.basicConfig(
        filename=str(resolved_dir / f"{log_name}.log"),
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    print(f"[Logging] Standalone logging configured: {resolved_dir / f'{log_name}.log'} (level={logging.getLevelName(level)})")

def setup_app_logging(log_name: str, log_dir: str | Path = "logs", level: int = logging.DEBUG):
    """
    Configure logging for the main application (e.g., in wsgi.py). Should be called before importing the app.
    Args:
        log_name (str): Name of the log file (without extension).
        log_dir (str | Path): Directory for log files (relative to project root).
        level (int): Logging level (default: DEBUG).
    """
    resolved_dir = _resolve_log_dir(log_dir)
    logging.basicConfig(
        filename=str(resolved_dir / f"{log_name}.log"),
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    print(f"[Logging] App logging configured: {resolved_dir / f'{log_name}.log'} (level={logging.getLevelName(level)})") 
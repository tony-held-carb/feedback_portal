"""
ARB Operator Feedback Portal app and related modules.

  - The project root directory is "feedback_portal"
  - if the app is run from wsgi.py file with path: feedback_portal/source/production/arb/wsgi.py
    - Path(__file__).resolve().parents[3] → .../feedback_portal
"""
from pathlib import Path
from arb.__get_logger import get_logger

__version__ = "1.0.0"

logger, pp_log = get_logger()

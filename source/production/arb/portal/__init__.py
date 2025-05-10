"""
ARB Operator Feedback Portal app and related modules.

  - The project root directory is "feedback_portal"
  - if the app is run from wsgi.py file with path: feedback_portal/source/production/arb/wsgi.py
    - Path(__file__).resolve().parents[3] → .../feedback_portal
"""
import arb.__get_logger as get_logger

__version__ = "1.0.0"


logger, pp_log = get_logger.get_logger(__name__, __file__)

# Get the platform independent project root directory knowing the apps directory structure is:
# 'feedback_portal/source/production/arb/portal/'


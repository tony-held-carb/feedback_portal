"""
ARB Operator Feedback Portal app and related modules.

"""
from pathlib import Path
from arb.__get_logger import get_logger

__version__ = "1.2.0"

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__)}"')


"""
Excel utilities input/output file structure.
"""

import arb.__get_logger as get_logger
from arb.utils.file_io import get_project_root_dir

logger, pp_log = get_logger.get_logger(__name__, __file__)

# Get the platform independent project root of the feedback portal
# The utility model may be initialized by running the module directly,
# or it may be initialized by a flask app.  Try to get the 'feedback_portal' either way

try:
  app_dir_structure = ['feedback_portal', 'source', 'production', 'arb', 'utils']
  PROJECT_ROOT = get_project_root_dir(__file__, app_dir_structure)
  logger.debug(f"{PROJECT_ROOT =}, determined by {app_dir_structure =}")
except ValueError as e:
  app_dir_structure = ['feedback_portal', 'source', 'production', 'arb', 'portal']
  PROJECT_ROOT = get_project_root_dir(__file__, app_dir_structure)
  logger.debug(f"{PROJECT_ROOT =}, determined by {app_dir_structure =}")

FEEDBACK_FORMS = PROJECT_ROOT / "feedback_forms"
CURRENT_VERSIONS = FEEDBACK_FORMS / "current_versions"
PROCESSED_VERSIONS = FEEDBACK_FORMS / "processed_versions"

logger.debug(f"{PROJECT_ROOT =}, {FEEDBACK_FORMS = }, {CURRENT_VERSIONS = }, {PROCESSED_VERSIONS = }")

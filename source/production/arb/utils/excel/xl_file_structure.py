"""
Module to store expected Excel file structure in a platform independent way.

Current directory structure:
feedback_portal             <-- base of project directory tree
 - feedback_forms
  - current_versions        <--  current versions of the feedback forms created in excel/vba
  - processed_versions      <--  updated versions of the "current versions" created in python
    - xl_payloads
    - xl_schemas
    - xl_workbooks
  - source
    - production
    - arb
      - portal
    - utils
      - excel

The goal of this module is to determine the path to feedback_portal in a platform independent way,
independent of whether this module was run from utils.excel directory or a flask app.
"""

import arb.__get_logger as get_logger
from arb.utils.file_io import get_project_root_dir

logger, pp_log = get_logger.get_logger(__name__, __file__)

try:
  # project is running from the utils.excel directory
  app_dir_structure = ['feedback_portal', 'source', 'production', 'arb', 'utils', 'excel']
  PROJECT_ROOT = get_project_root_dir(__file__, app_dir_structure)
  logger.debug(f"{PROJECT_ROOT =}, determined by {__file__ =} and {app_dir_structure =}")
except ValueError as e:
  # project is running from the portal flask app
  app_dir_structure = ['feedback_portal', 'source', 'production', 'arb', 'portal']
  PROJECT_ROOT = get_project_root_dir(__file__, app_dir_structure)
  logger.debug(f"{PROJECT_ROOT =}, determined by {__file__ =} and {app_dir_structure =}")

FEEDBACK_FORMS = PROJECT_ROOT / "feedback_forms"
CURRENT_VERSIONS = FEEDBACK_FORMS / "current_versions"
PROCESSED_VERSIONS = FEEDBACK_FORMS / "processed_versions"

logger.debug(f"{PROJECT_ROOT =}, {FEEDBACK_FORMS = }, {CURRENT_VERSIONS = }, {PROCESSED_VERSIONS = }")

"""
Excel utilities input/output file structure.
"""

import arb.__get_logger as get_logger
from arb.utils.file_io import get_project_root_dir

logger, pp_log = get_logger.get_logger(__name__, __file__)

# Get the platform independent project root directory knowing the utils directory structure is:
# 'feedback_portal/source/production/arb/utils/'
app_dir_structure = ['feedback_portal', 'source', 'production', 'arb', 'utils']
PROJECT_ROOT = get_project_root_dir(__file__, app_dir_structure)
FEEDBACK_FORMS = PROJECT_ROOT / "feedback_forms"
CURRENT_VERSIONS = FEEDBACK_FORMS / "current_versions"
PROCESSED_VERSIONS = FEEDBACK_FORMS / "processed_versions"

logger.debug(f"{PROJECT_ROOT =}, {FEEDBACK_FORMS = }, {CURRENT_VERSIONS = }, {PROCESSED_VERSIONS = }")

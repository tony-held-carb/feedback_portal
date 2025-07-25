"""
Module to determine the path to the root of the feedback_portal project in a platform-independent way.

This module can be invoked from multiple runtime contexts, including:
- The `utils.excel` directory (e.g., for standalone Excel/VBA payload generation).
- The `portal` Flask app directory.

Directory structure reference:

/feedback_portal/                   <-- Base of project directory tree
  ├── feedback_forms/
       ├── current_versions/        <-- Current versions of feedback forms (created in Excel/VBA)
       └── processed_versions/      <-- Updated versions created in Python
            ├── xl_payloads/
            ├── xl_schemas/
            └── xl_workbooks/
  ├── source/
       └── production/
            └── arb/
                 ├── portal/        <-- Flask app
                 └── utils/
                      └── excel/    <-- Excel generation scripts

Attributes:
  PROJECT_ROOT (Path): Resolved root directory of the project.
  FEEDBACK_FORMS (Path): Path to the 'feedback_forms' directory.
  CURRENT_VERSIONS (Path): Path to Excel files from current official versions.
  PROCESSED_VERSIONS (Path): Path to output files generated via Python processing.
"""

import logging

from arb.utils.file_io import resolve_project_root

logger = logging.getLogger(__name__)

# directory structures that contain the project root
candidate_structures = [
  ['feedback_portal', 'source', 'production', 'arb', 'utils', 'excel'],
  ['feedback_portal', 'source', 'production', 'arb', 'portal'],
]

# Set project root and derived paths
PROJECT_ROOT = resolve_project_root(__file__, candidate_structures)

FEEDBACK_FORMS = PROJECT_ROOT / "feedback_forms"
CURRENT_VERSIONS = FEEDBACK_FORMS / "current_versions"
PROCESSED_VERSIONS = FEEDBACK_FORMS / "processed_versions"

logger.debug(f"{PROJECT_ROOT =}, {FEEDBACK_FORMS =}, {CURRENT_VERSIONS =}, {PROCESSED_VERSIONS =}")

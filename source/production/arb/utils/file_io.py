"""
Utility functions for file and path handling, including directory creation,
secure file name generation, and project root resolution.

Features:
- Ensures parent and target directories exist
- Generates secure, timestamped file names using UTC
- Dynamically resolves the project root based on directory structure
- Includes diagnostics for local testing and validation

Notes:
- Uses `werkzeug.utils.secure_filename` to sanitize input filenames
- Timestamps are formatted in UTC using the DATETIME_WITH_SECONDS pattern

Potential Future Upgrades:
- Add support for Windows-specific path edge cases, if needed.
- Expand run_diagnostics to perform write/delete tests in a sandbox directory.
"""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from werkzeug.utils import secure_filename

from arb.__get_logger import get_logger
from arb.portal.constants import DATETIME_WITH_SECONDS

__version__ = "1.0.0"
logger, pp_log = get_logger()


def ensure_parent_dirs(file_name: str | Path) -> None:
  """
  Ensure that the parent directories for a given file path exist.

  Args:
      file_name (str | Path): The full path to a file. Parent folders will be created if needed.

  Returns:
      None
  Example:
      >>> ensure_parent_dirs("/tmp/some/deep/file.txt")
      >>> ensure_parent_dirs("local_file.txt")
  """
  logger.debug(f"ensure_parent_dirs() called for: {file_name=}")
  file_path = Path(file_name)
  file_path.parent.mkdir(parents=True, exist_ok=True)


def ensure_dir_exists(dir_path: str | Path) -> None:
  """
  Ensure that the specified directory exists, creating it if necessary.

  Args:
      dir_path (str | Path): Path to the directory.

  Raises:
      ValueError: If the path exists but is not a directory.

  Returns:
      None

  Example:
      >>> ensure_dir_exists("logs/output")
  """
  logger.debug(f"ensure_dir_exists() called for: {dir_path=}")
  dir_path = Path(dir_path)

  if dir_path.exists() and not dir_path.is_dir():
    raise ValueError(f"The path {dir_path} exists and is not a directory.")

  dir_path.mkdir(parents=True, exist_ok=True)


def get_secure_timestamped_file_name(directory: str | Path, file_name: str) -> Path:
  """
  Generate a sanitized file name in the given directory, appending a UTC timestamp.

  Args:
      directory (str | Path): Target directory where the file will be saved.
      file_name (str): Proposed name for the file, possibly unsafe.

  Returns:
      Path: The full secure, timestamped file path.

  Example:
      >>> get_secure_timestamped_file_name("/tmp", "user report.xlsx")
      Path("/home/user/tmp/user_report_ts_2025-05-05T12-30-00Z.xlsx")
  """
  file_name_clean = secure_filename(file_name)
  full_path = Path.home() / directory / file_name_clean

  timestamp = datetime.now(ZoneInfo("UTC")).strftime(DATETIME_WITH_SECONDS)
  new_name = f"{full_path.stem}_ts_{timestamp}{full_path.suffix}"

  return full_path.with_name(new_name)


class ProjectRootNotFoundError(ValueError):
  """
  Raised when no matching project root can be determined from the provided file path
  and candidate folder sequences.
  """
  pass


def resolve_project_root(
    file_path: str | Path,
    candidate_structures: list[list[str]] | None = None
) -> Path:
  """
  Attempt to locate the project root directory using known folder sequences.

  Args:
      file_path (str | Path): The file path to begin traversal from (typically `__file__`).
      candidate_structures (list[list[str]] | None): List of folder name sequences to match.

  Returns:
      Path: Path to the root of the matched folder chain.

  Raises:
      ProjectRootNotFoundError: If no matching sequence is found.

  Example:
      >>> resolve_project_root(__file__)
      Path("/Users/tony/dev/feedback_portal")
  """
  if candidate_structures is None:
    candidate_structures = [
      ['feedback_portal', 'source', 'production', 'arb', 'utils', 'excel'],
      ['feedback_portal', 'source', 'production', 'arb', 'portal'],
    ]

  errors = []
  for structure in candidate_structures:
    try:
      root = get_project_root_dir(file_path, structure)
      logger.debug(f"{root =}, based on structure {structure =}")
      return root
    except ValueError as e:
      errors.append(f"{structure}: {e}")

  raise ProjectRootNotFoundError(
    "Unable to determine project root. Tried the following structures:\n" +
    "\n".join(errors)
  )


def get_project_root_dir(file: str | Path, match_parts: list[str]) -> Path:
  """
  Traverse up the directory tree from a file path to locate the root of a known structure.

  Args:
      file (str | Path): The starting file path, typically `__file__`.
      match_parts (list[str]): Folder names expected in the path, ordered from root to leaf.

  Returns:
      Path: Path to the top of the matched folder chain.

  Raises:
      ValueError: If no matching structure is found in the parent hierarchy.

  Passing Example:
    If `file = "/Users/tony/dev/feedback_portal/source/production/arb/portal/config.py"`
    and `match_parts = ["feedback_portal", "source", "production", "arb", "portal"]`,
    then:
      → match found at /Users/tony/dev/**feedback_portal**/source/production/arb/portal
      → returns: Path("/Users/tony/dev/feedback_portal")

  Failing Example:
    If the file path is unrelated (e.g., "/tmp/random_file.py"),
    the function will raise a ValueError.
  """
  path = Path(file).resolve()
  match_len = len(match_parts)

  current = path
  while current != current.parent:
    if list(current.parts[-match_len:]) == match_parts:
      return Path(*current.parts[:len(current.parts) - match_len + 1])
    current = current.parent

  raise ValueError(f"Could not locate project root using match_parts={match_parts} from path={path}")


def run_diagnostics() -> None:
  """
  Run a series of checks to validate directory creation, secure filename generation,
  and project root resolution logic.

  Returns:
      None
  """
  import tempfile

  print("Running diagnostics...")

  # Test ensure_dir_exists
  test_dir = Path(tempfile.gettempdir()) / "arb_test_nested/subdir"
  ensure_dir_exists(test_dir)
  assert test_dir.exists() and test_dir.is_dir()

  # Test ensure_parent_dirs
  test_file = test_dir / "test_file.txt"
  ensure_parent_dirs(test_file)
  assert test_file.parent.exists()

  # Test secure file name generation
  secured_path = get_secure_timestamped_file_name(test_dir, "My Unsafe Report.xlsx")
  print(f"Generated secure file: {secured_path}")
  assert secured_path.name.startswith("My_Unsafe_Report_ts_")

  # Test project root resolution
  try:
    project_root = resolve_project_root(__file__)
    print(f"Resolved project root: {project_root}")
    assert project_root.exists()
  except ProjectRootNotFoundError as e:
    print("WARNING: Could not resolve project root. Skipping root validation.")

  print("All diagnostics completed successfully.")


if __name__ == "__main__":
  run_diagnostics()

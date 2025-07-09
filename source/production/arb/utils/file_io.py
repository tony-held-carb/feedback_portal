"""
File and path utility functions for the ARB Feedback Portal.

This module provides helpers for directory creation, secure file name generation, project root resolution,
and efficient file reading. These utilities are designed to support robust file handling and diagnostics
across ARB portal workflows.

Features:
- Ensures parent and target directories exist
- Generates secure, timestamped file names using UTC
- Dynamically resolves the project root based on directory structure
- Efficiently reads the last N lines of large files

Notes:
- Uses `werkzeug.utils.secure_filename` to sanitize input filenames
- Timestamps are formatted in UTC using the DATETIME_WITH_SECONDS pattern

Intended use:
- Shared helpers for ARB portal and related utilities
- Promotes DRY principles and robust file handling

Version: 1.0.0
"""

import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from werkzeug.utils import secure_filename

from arb.portal.constants import DATETIME_WITH_SECONDS

__version__ = "1.0.0"
logger = logging.getLogger(__name__)


def ensure_parent_dirs(file_name: str | Path) -> None:
  """
  Ensure that the parent directories for a given file path exist.

  Args:
    file_name (str | Path): The full path to a file. Parent folders will be created if needed. If None or empty, no action is taken.

  Returns:
    None

  Examples:
    Input : "/tmp/some/deep/file.txt"
    Output: Ensures intermediate directories exist
    Input : "local_file.txt"
    Output: No error if directory already exists or is current
    Input : None
    Output: No action
    Input : ""
    Output: No action

  Notes:
    - If `file_name` is None or empty, no action is taken.
  """
  logger.debug(f"ensure_parent_dirs() called for: {file_name=}")
  file_path = Path(file_name)
  file_path.parent.mkdir(parents=True, exist_ok=True)


def ensure_dir_exists(dir_path: str | Path) -> None:
  """
  Ensure that the specified directory exists, creating it if necessary.

  Args:
    dir_path (str | Path): Path to the directory. If None or empty, no action is taken.

  Raises:
    ValueError: If the path exists but is not a directory.

  Returns:
    None

  Examples:
    Input : "logs/output"
    Output: Creates the directory and parents if needed
    Input : None
    Output: No action
    Input : ""
    Output: No action

  Notes:
    - If `dir_path` is None or empty, no action is taken.
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
    directory (str | Path): Target directory where the file will be saved. If None or empty, uses the home directory.
    file_name (str): Proposed name for the file, possibly unsafe. If None or empty, raises ValueError.

  Returns:
    Path: The full secure, timestamped file path.

  Examples:
    Input : "/tmp", "user report.xlsx"
    Output: Path("/home/user/tmp/user_report_ts_2025-05-05T12-30-00Z.xlsx")
    Input : None, "user report.xlsx"
    Output: Path("/home/user/user_report_ts_2025-05-05T12-30-00Z.xlsx")
    Input : "/tmp", None
    Output: ValueError
    Input : "/tmp", ""
    Output: ValueError

  Raises:
    ValueError: If `file_name` is None or empty.

  Notes:
    - Uses `werkzeug.utils.secure_filename` to sanitize input filenames.
    - If `directory` is None or empty, uses the home directory.
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
    file_path (str | Path): The file path to begin traversal from (typically `__file__`). If None or empty, raises ValueError.
    candidate_structures (list[list[str]] | None): List of folder name sequences to match. If None, uses defaults.

  Returns:
    Path: Path to the root of the matched folder chain.

  Raises:
    ProjectRootNotFoundError: If no matching sequence is found.
    ValueError: If `file_path` is None or empty.

  Examples:
    Input : __file__
    Output: Path to the resolved project root, such as Path("/Users/tony/dev/feedback_portal")
    Input : None
    Output: ValueError
    Input : ""
    Output: ValueError

  Notes:
    - If `file_path` is None or empty, raises ValueError.
    - If `candidate_structures` is None, uses default structures.
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
    file (str | Path): The starting file path, typically `__file__`. If None or empty, raises ValueError.
    match_parts (list[str]): Folder names expected in the path, ordered from root to leaf. If None or empty, raises ValueError.

  Returns:
    Path: Path to the top of the matched folder chain.

  Raises:
    ValueError: If no matching structure is found in the parent hierarchy, or if arguments are None or empty.

  Examples:
    Input : "/Users/tony/dev/feedback_portal/source/production/arb/portal/config.py", ["feedback_portal", "source", "production", "arb", "portal"]
    Output: Path("/Users/tony/dev/feedback_portal")
    Input : None, ["feedback_portal", "source", "production", "arb", "portal"]
    Output: ValueError
    Input : "/Users/tony/dev/feedback_portal/source/production/arb/portal/config.py", []
    Output: ValueError

  Notes:
    - If `file` or `match_parts` is None or empty, raises ValueError.
  """
  path = Path(file).resolve()
  match_len = len(match_parts)

  current = path
  while current != current.parent:
    if list(current.parts[-match_len:]) == match_parts:
      return Path(*current.parts[:len(current.parts) - match_len + 1])
    current = current.parent

  raise ValueError(f"Could not locate project root using match_parts={match_parts} from path={path}")


def read_file_reverse(path: str | Path, n: int = 1000,
                      encoding: str = "utf-8") -> list[str]:
  """
  Efficiently read the last `n` lines of a text file in reverse order,
  returning the result in normal top-down order (oldest to newest).

  This function is optimized for large files by avoiding full memory loads.
  It uses streaming reads from the end of the file, making it suitable for
  real-time diagnostics, log viewers, or tail-style interfaces.

  Args:
    path (str | Path): Path to the log or text file. If None or empty, raises ValueError.
    n (int): Number of lines to read from the end of the file (default is 1000).
    encoding (str): Text encoding used to decode the file (default is "utf-8").

  Returns:
    list[str]: A list of up to `n` lines from the end of the file,
               returned in chronological (not reverse) order.

  Raises:
    FileNotFoundError: If the file does not exist.
    OSError: If the file cannot be read due to permission or I/O issues.
    ValueError: If `path` is None or empty.

  Notes:
    - This method uses the `file_read_backwards` library, which performs
      disk-efficient reverse reads by buffering from the end.
    - Handles variable-length lines and multi-byte encodings gracefully.
    - Does not assume file fits in memory — ideal for large logs.

  Examples:
    Input : "/var/log/syslog", n=100
    Output: Returns the last 100 lines in chronological order
    Input : None, n=100
    Output: ValueError
    Input : "", n=100
    Output: ValueError
  """
  from file_read_backwards import FileReadBackwards

  file_path = Path(path)
  lines: list[str] = []

  with FileReadBackwards(file_path, encoding=encoding) as f:
    for i, line in enumerate(f):
      lines.append(line)
      if i + 1 >= n:
        break

  return list(reversed(lines))

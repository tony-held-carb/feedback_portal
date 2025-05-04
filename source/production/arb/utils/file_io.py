from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from werkzeug.utils import secure_filename

from arb.__get_logger import get_logger
from arb.portal.constants import DATETIME_WITH_SECONDS

__version__ = "1.0.0"
logger, pp_log = get_logger(__name__, __file__)


def ensure_parent_dirs(file_name):
  """
  Ensure the parent directories of the given file path exist.

  Args:
      file_name (str or pathlib.Path): A relative or absolute file path.

  Notes:

  Example usage:
      ensure_parents("/path/to/some/directory/file.txt")
      ensure_parents("file.txt")
  """
  logger.debug(f"ensure_parent_dirs() called to ensure parent directories exist for: {file_name=}")

  # Convert to a Path object if it's a string
  file_path = Path(file_name)

  # Create parent directories if they don't exist
  file_path.parent.mkdir(parents=True, exist_ok=True)


def ensure_dir_exists(dir_path):
  """
  Ensures that the specified directory exists, creating it if necessary.

  Args:
      dir_path (str or pathlib.Path): The path to the directory to check or create.

  Raises:
      ValueError: If the provided path is not a directory.

  Example usage:
    ensure_directory_exists("some/nested/directory")
    ensure_directory_exists(Path("another/directory"))

  """
  logger.debug(f"ensure_dir_exists() called to ensure parent directories exist for: {dir_path=}")

  # Convert string to Path if necessary
  dir_path = Path(dir_path)

  # Check if the path points to a directory
  if dir_path.exists() and not dir_path.is_dir():
    raise ValueError(f"The path {dir_path} exists and is not a directory.")

  # Create the directory if it doesn't exist
  dir_path.mkdir(parents=True, exist_ok=True)


def get_secure_timestamped_file_name(directory, file_name):
  """
  Get a fully specified file name that is secure (no special characters) with a timestamp based on
  a desired directory and proposed filename (that may have special characters).

  Args:
    directory (str|Path): target directory
    file_name (str): initial proposed filename

  Returns (Path): fully specified file name
  """

  # logger.debug(f"{directory=}, {file_name=}")
  file_name_as_str = secure_filename(file_name)
  file_name_as_path = Path.home().joinpath(directory, file_name_as_str)

  file_stem = file_name_as_path.stem
  time_stamp = datetime.now(ZoneInfo("UTC")).strftime(DATETIME_WITH_SECONDS)
  file_name_as_path = file_name_as_path.with_stem(file_stem + "_ts_" + time_stamp)
  # logger.debug(f"{file_stem=}, {time_stamp=}, {file_name_as_path=}")

  return file_name_as_path


from pathlib import Path


def get_project_root_dir(file, match_parts):
  """
  Locate the project root directory by walking up from a given file path and identifying
  a directory whose trailing path components match a known directory structure.

  Unlike typical suffix matchers that return the leaf folder, this function returns the
  root of the matched structure — i.e., the top-most directory in `match_parts`.

  Args:
    file (str | Path): The path of a file within the project. Typically `__file__`.
    match_parts (List[str]): A list of directory names representing a known path suffix,
                             ordered from project root to leaf. For example:
                             ["feedback_portal", "source", "production", "arb", "portal"]

  Returns:
    Path: A `Path` object pointing to the root of the matched structure — the first component
          in the `match_parts` list.

  Raises:
    ValueError: If the specified directory sequence is not found in the parent hierarchy.

  Logic:
    - Resolve the input path.
    - Walk upward through its parents using `.parent`.
    - At each step, check if the trailing parts of the path match `match_parts`.
    - If matched, return the path slice up to the beginning of the match.

  Discussion:
    - `current.parts` returns a tuple of strings representing the components of the path.
      For example:
        Path("/a/b/c/d.py").parts → ('/', 'a', 'b', 'c', 'd.py')
    - This allows easy inspection and slicing of the directory structure.

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
    parts = current.parts
    if list(parts[-match_len:]) == match_parts:
      # Get the path up to the start of the match
      return Path(*parts[:len(parts) - match_len + 1])
    current = current.parent

  raise ValueError(f"Could not locate project root using match sequence {match_parts} from {path}")


if __name__ == "__main__":
  pass

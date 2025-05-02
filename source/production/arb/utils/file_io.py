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


if __name__ == "__main__":
  pass


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

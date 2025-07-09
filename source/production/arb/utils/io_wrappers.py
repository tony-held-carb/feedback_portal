"""
File I/O utility wrappers for the ARB Feedback Portal.

This module provides reusable helpers for safely reading and writing JSON and text files, as well as
copying files with directory creation. These functions isolate file system side effects and should be
used anywhere file persistence is required in ARB portal utilities or scripts.

Features:
- Simplifies error handling and directory setup
- Makes code easier to test and mock
- Promotes DRY principles for common file tasks

Typical usage:
    from arb.utils.io_wrappers import save_json_safely, read_json_file
    save_json_safely(data, Path("/tmp/output.json"))
    contents = read_json_file(Path("/tmp/output.json"))

Version: 1.0.0
"""

import json
from pathlib import Path
from shutil import copy2


def save_json_safely(
    data: object,
    path: Path,
    encoding: str = "utf-8",
    json_options: dict | None = None
) -> None:
  """
  Write a dictionary as JSON to the specified path with optional encoding and json options.

  Args:
    data (object): Data to serialize. If None, writes 'null' to the file.
    path (Path): Destination file path. If None, raises ValueError.
    encoding (str): File encoding (default: "utf-8").
    json_options (dict | None): Options passed to `json.dump` (e.g., indent, default).

  Raises:
    OSError: If the file or directory cannot be written.
    ValueError: If `path` is None.

  Examples:
    Input : {"a": 1}, Path("/tmp/test.json")
    Output: Writes JSON to /tmp/test.json

  Notes:
    - If `data` is None, writes 'null' to the file.
    - If `path` is None, raises ValueError.
  """
  if path is None:
    raise ValueError("Path must not be None.")
  json_options = json_options or {"indent": 2}
  path.parent.mkdir(parents=True, exist_ok=True)
  with path.open("w", encoding=encoding) as f:
    json.dump(data, f, **json_options)


def read_json_file(
    path: Path,
    encoding: str = "utf-8-sig",
    json_options: dict | None = None
) -> dict:
  """
  Load and return the contents of a JSON file.

  Args:
    path (Path): Path to the JSON file. If None, raises ValueError.
    encoding (str): File encoding (default: "utf-8-sig" to handle BOM).
    json_options (dict | None): Options passed to `json.load` (e.g., object_hook).

  Returns:
    dict: Parsed JSON contents.

  Raises:
    FileNotFoundError: If the file does not exist.
    json.JSONDecodeError: If the file is not valid JSON.
    ValueError: If `path` is None.

  Examples:
    Input : Path("/tmp/test.json")
    Output: Returns parsed JSON dict

  Notes:
    - If `path` is None, raises ValueError.
  """
  if path is None:
    raise ValueError("Path must not be None.")
  json_options = json_options or {}
  with path.open("r", encoding=encoding) as f:
    return json.load(f, **json_options)


def write_text_file(text: str, path: Path, encoding: str = "utf-8") -> None:
  """
  Write plain text to a file, overwriting if it exists.

  Args:
    text (str): Text content to write. If None, writes an empty file.
    path (Path): Destination file path. If None, raises ValueError.
    encoding (str): File encoding (default: "utf-8").

  Raises:
    OSError: If the file cannot be written.
    ValueError: If `path` is None.

  Examples:
    Input : "Hello, world!", Path("/tmp/hello.txt")
    Output: Writes text to /tmp/hello.txt

  Notes:
    - If `text` is None, writes an empty file.
    - If `path` is None, raises ValueError.
  """
  if path is None:
    raise ValueError("Path must not be None.")
  if text is None:
    text = ""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text, encoding=encoding)


def copy_file_safe(src: Path, dst: Path) -> None:
  """
  Copy a file from `src` to `dst`, creating the destination directory if needed.

  Args:
    src (Path): Source file path. If None, raises ValueError.
    dst (Path): Destination file path. If None, raises ValueError.

  Raises:
    FileNotFoundError: If the source file does not exist.
    OSError: If the copy fails.
    ValueError: If `src` or `dst` is None.

  Examples:
    Input : Path("/tmp/a.txt"), Path("/tmp/b.txt")
    Output: Copies a.txt to b.txt

  Notes:
    - If `src` or `dst` is None, raises ValueError.
  """
  if src is None or dst is None:
    raise ValueError("src and dst must not be None.")
  dst.parent.mkdir(parents=True, exist_ok=True)
  copy2(src, dst)

"""
Generate GitHub-style raw file metadata across all local branches.

Scans all non-skipped local Git branches and collects metadata for each tracked file,
including its blob SHA and size. Outputs a CSV snapshot in the project root under
the folder `repo_file_index`, named using the repository and a UTC timestamp.

Example output:
  repo_file_index/feedback_portal_snapshot_20250615T144558Z.csv

Requires:
  - Git must be installed and available on the PATH.
  - Script must be run within a Git repository.

Author: OpenAI ChatGPT
"""

import subprocess
import csv
import os
import time
from datetime import datetime
from pathlib import Path

# === CONFIGURATION ===
GITHUB_USER = "tony-held-carb"
GITHUB_REPO = "feedback_portal"
SKIP_BRANCHES = {"gh-pages"}
OUTPUT_DIR = Path("repo_file_index")  # always relative to repo root
# ======================


def run_cmd(args: list[str], cwd: Path = None) -> str:
  """Run a shell command and return stdout as a string."""
  result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True)
  return result.stdout.strip()


def get_repo_root() -> Path:
  """Return the absolute path to the root of the current Git repository."""
  return Path(run_cmd(["git", "rev-parse", "--show-toplevel"]))


def list_local_branches() -> list[str]:
  """List all local Git branches (excluding SKIP_BRANCHES)."""
  output = run_cmd(["git", "branch", "--format", "%(refname:short)"])
  return [line.strip() for line in output.splitlines() if line.strip() not in SKIP_BRANCHES]


def list_files_in_branch(branch: str) -> list[tuple[str, str, str]]:
  """
  List all tracked files in a branch.

  Returns:
    list[tuple[str, str, str]]: (path, sha, size) for each file
  """
  output = run_cmd(["git", "ls-tree", "-lr", branch])
  entries = []
  for line in output.splitlines():
    if '\t' not in line:
      continue
    meta, path = line.split('\t', 1)
    parts = meta.split()
    if len(parts) >= 4:
      sha = parts[2]
      size = parts[3]
      entries.append((path, sha, size))
  return entries


def build_raw_url(branch: str, path: str) -> str:
  """Build raw.githubusercontent.com URL for a given branch and path."""
  return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{branch}/{path}"


def generate_metadata_csv(repo_root: Path) -> Path:
  """Generate the file metadata snapshot and write to CSV."""
  start = time.time()
  utc_now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

  out_dir = repo_root / OUTPUT_DIR
  out_dir.mkdir(parents=True, exist_ok=True)

  out_file = out_dir / f"{GITHUB_REPO}_snapshot_{utc_now}.csv"
  print(f"\nNow create file named: {out_file}\n")

  with out_file.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["branch", "path", "raw_url", "sha (blob id)", "size (bytes)"])

    branches = list_local_branches()
    for branch in branches:
      print(f"Processing branch: {branch}")
      try:
        entries = list_files_in_branch(branch)
        print(f"  Found {len(entries)} files")
        for path, sha, size in entries:
          writer.writerow([branch, path, build_raw_url(branch, path), sha, size])
      except subprocess.CalledProcessError as e:
        print(f"Error in branch {branch}: {e}")

  end = time.time()
  start_dt = datetime.utcfromtimestamp(start)
  end_dt = datetime.utcfromtimestamp(end)
  duration = end - start

  print("\n    Metadata snapshot complete.")
  print(f"   Started:   {start_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
  print(f"   Finished:  {end_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
  print(f"   Duration:  {duration:.2f} seconds")

  # 👇 Final line is path to allow post-commit to capture it
  # print(out_file.resolve())  # safer than str(out_file) for absolute path

  return out_file


if __name__ == "__main__":
  repo_root = get_repo_root()
  os.chdir(repo_root)
  generate_metadata_csv(repo_root)

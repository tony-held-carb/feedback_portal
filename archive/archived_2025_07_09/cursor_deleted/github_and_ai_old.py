import requests
from datetime import datetime
from pathlib import Path


def list_branches(user: str, repo: str) -> list[str]:
  """
  List all branches in a public GitHub repository.

  Args:
    user (str): GitHub username or organization.
    repo (str): Repository name.

  Returns:
    list[str]: Branch names.
  """
  url = f"https://api.github.com/repos/{user}/{repo}/branches"
  response = requests.get(url)
  response.raise_for_status()
  return [branch["name"] for branch in response.json()]


def get_raw_file_urls(user: str, repo: str, branch: str) -> list[tuple[str, str]]:
  """
  Get a list of (path, raw_url) tuples for all files in a branch.

  Args:
    user (str): GitHub username or organization.
    repo (str): Repository name.
    branch (str): Branch name.

  Returns:
    list[tuple[str, str]]: Each tuple contains (path, raw_url).
  """
  api_url = f"https://api.github.com/repos/{user}/{repo}/git/trees/{branch}?recursive=1"
  raw_prefix = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/"

  response = requests.get(api_url)
  response.raise_for_status()
  tree = response.json().get("tree", [])
  return [(item["path"], raw_prefix + item["path"]) for item in tree if item["type"] == "blob"]


def write_combined_url_file(user: str,
                            repo: str,
                            output_dir: Path = Path("."),
                            skip_branches: list[str] = None) -> Path:
  """
  Write a combined URL list across all branches to a single CSV-style text file.

  Args:
    user (str): GitHub username or organization.
    repo (str): Repository name.
    output_dir (Path): Output directory.
    skip_branches (list[str], optional): Branches to skip.

  Returns:
    Path: Path to the output file.
  """
  if skip_branches is None:
    skip_branches = ["gh-pages"]

  timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
  output_path = output_dir / f"raw_file_urls_all_branches_{timestamp}.txt"
  print(f"\nNow create file named: {output_path}\n")

  branches = list_branches(user, repo)

  with open(output_path, "w", encoding="utf-8") as f:
    f.write("branch,path,raw_url\n")  # CSV header
    for branch in branches:
      if branch in skip_branches:
        print(f"Skipping branch: {branch}")
        continue
      print(f"Processing branch: {branch}")
      try:
        entries = get_raw_file_urls(user, repo, branch)
        print(f"  Found {len(entries)} files in {branch}")
        for path, url in entries:
          f.write(f"{branch},{path},{url}\n")
      except requests.HTTPError as e:
        print(f"  Failed to process {branch}: {e}")

  return output_path


# Example usage:
if __name__ == "__main__":
  write_combined_url_file("tony-held-carb", "feedback_portal")

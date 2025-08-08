import os
import subprocess
import sys

import yaml

YML_PATH = os.path.join(os.path.dirname(__file__), '..', 'admin', 'mini_conda_01.yml')


# Detect conda executable path based on platform
def get_conda_exe():
  """Detect conda executable path based on platform and common locations."""
  if sys.platform.startswith('win'):
    # Windows paths
    possible_paths = [
      r"C:\Users\tonyh\miniconda3\condabin\conda.bat",
      r"C:\Users\theld\AppData\Local\miniconda3\condabin\conda.bat",
      r"C:\ProgramData\miniconda3\condabin\conda.bat",
    ]
  else:
    # Linux/Unix paths
    possible_paths = [
      "/home/theld/miniconda3/bin/conda",
      "/home/tonyh/miniconda3/bin/conda",
      "/opt/conda/bin/conda",
    ]

  for path in possible_paths:
    if os.path.exists(path):
      return path

  # Fallback: try to find conda in PATH
  try:
    result = subprocess.run(['which', 'conda'], capture_output=True, text=True)
    if result.returncode == 0:
      return result.stdout.strip()
  except FileNotFoundError:
    pass

  return None


CONDA_EXE = get_conda_exe()


def get_pip_freeze():
  result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
  pkgs = set()
  for line in result.stdout.splitlines():
    if '==' in line:
      pkgs.add(line.split('==')[0].lower())
    elif '@' in line:
      pkgs.add(line.split('@')[0].strip().lower())
  return pkgs


def get_conda_list():
  if not CONDA_EXE:
    print("ERROR: Could not find conda executable. Please check your conda installation.")
    return set()

  try:
    result = subprocess.run([CONDA_EXE, 'list', '--export'], capture_output=True, text=True, check=True)
  except FileNotFoundError:
    print(f"ERROR: Could not find conda at {CONDA_EXE}. Please check the path.")
    return set()
  except subprocess.CalledProcessError as e:
    print(f"ERROR: Conda command failed: {e}")
    return set()
  pkgs = set()
  for line in result.stdout.splitlines():
    if not line or line.startswith('#'):
      continue
    if '=' in line:
      pkgs.add(line.split('=')[0].lower())
  return pkgs


def parse_yml(yml_path):
  with open(yml_path, 'r', encoding='utf-8') as f:
    yml = yaml.safe_load(f)
  conda_pkgs = set()
  pip_pkgs = set()
  for dep in yml.get('dependencies', []):
    if isinstance(dep, str):
      # conda package
      if '=' in dep:
        conda_pkgs.add(dep.split('=')[0].lower())
      else:
        conda_pkgs.add(dep.lower())
    elif isinstance(dep, dict) and 'pip' in dep:
      for pip_pkg in dep['pip']:
        if '==' in pip_pkg:
          pip_pkgs.add(pip_pkg.split('==')[0].lower())
        elif '[' in pip_pkg:
          pip_pkgs.add(pip_pkg.split('[')[0].lower())
        else:
          pip_pkgs.add(pip_pkg.lower())
  return conda_pkgs, pip_pkgs


def main():
  print(f"Comparing current environment to YAML: {YML_PATH}\n")
  pip_env = get_pip_freeze()
  conda_env = get_conda_list()
  conda_yml, pip_yml = parse_yml(YML_PATH)

  missing_pip = pip_env - pip_yml
  missing_conda = conda_env - conda_yml

  print("Packages in current environment but missing from YAML:")
  print("\n[Conda packages]")
  if missing_conda:
    for pkg in sorted(missing_conda):
      print(f"  {pkg}")
  else:
    print("  None")

  print("\n[Pip packages]")
  if missing_pip:
    for pkg in sorted(missing_pip):
      print(f"  {pkg}")
  else:
    print("  None")

  print("\nDone.")


if __name__ == '__main__':
  main()

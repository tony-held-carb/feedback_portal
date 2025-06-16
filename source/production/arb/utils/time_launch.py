"""
time_launch.py - Script to measure runtime duration of a simple Python script.

Purpose:
  - Helps compare total wall-clock time between running in PyCharm vs. CMD.
  - Includes artificial 3-second delay via time.sleep.

Usage:
  python time_launch.py

Notes:
  - Captures wall-clock duration from Python entrypoint to end.
  - To capture interpreter *startup overhead*, see advice below.

Author: Your Name
"""

import sys

print("=== PRE-IMPORT MODULE SCAN ===")
for name in sorted(sys.modules):
  if "pycharm" in name or "datalore" in name or "pydev" in name:
    print(" [AUTO-LOADED]", name)

import time
import platform

start = time.perf_counter()

print(f"[INFO] Python version: {platform.python_version()} on {platform.system()}")
print(f"[INFO] Script started at {time.strftime('%X')}")

time.sleep(3.0)

end = time.perf_counter()
duration = end - start

print(f"[INFO] Script completed at {time.strftime('%X')}")
print(f"[RESULT] Total script runtime: {duration:.4f} seconds")

import subprocess
from pathlib import Path
from datetime import datetime
import sys
from typing import Optional

# Note: xlrdiff must be installed and available in your PATH.
# You may need to install it via pip (pip install xlrdiff) and ensure you use xlrdiff <=1.2.0 for .xlsx support.
# See: https://github.com/andrewcooke/xlrdiff


def run_xlrdiff(file_a: Path, file_b: Path, output_path: Optional[Path] = None) -> str:
    """
    Run xlrdiff on two Excel files and return the diff output as a string.
    If output_path is provided, write the diff to that file.
    """
    cmd = [sys.executable, '-m', 'xlrdiff', str(file_a), str(file_b)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        diff_output = result.stdout
        if output_path is not None:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(diff_output)
        return diff_output
    except subprocess.CalledProcessError as e:
        print(f"Error running xlrdiff: {e.stderr}")
        return ""


def compare_excel_files(file_a: Path, file_b: Path, log_to_file: bool = True) -> str:
    """
    Compare two Excel files using xlrdiff and output a human-readable summary of differences.
    Mimics the structure of excel_compare.py.
    """
    now = datetime.now()
    out_path: Optional[Path] = Path(f"comparison_xlrdiff_at_{now.strftime('%Y%m%d_%H%M%S')}.txt") if log_to_file else None
    print(f"Comparing:\n  A: {file_a}\n  B: {file_b}")
    diff_output = run_xlrdiff(file_a, file_b, output_path=out_path)
    if not diff_output:
        print("No differences found or error running xlrdiff.")
    else:
        print("Diff written to:", out_path)
    return diff_output


def main():
    # Example usage: update these paths as needed
    file_a = Path(r"D:/local/cursor/feedback_portal/diagnostics/dairy_digester_operator_feedback_v006_for_review_local.xlsx")
    file_b = Path(r"D:/local/cursor/feedback_portal/diagnostics/dairy_digester_operator_feedback_v006_for_review_sharepoint.xlsx")
    compare_excel_files(file_a, file_b, log_to_file=True)


if __name__ == "__main__":
    main()

# Limitations:
# - xlrdiff (and xlrd) may not support all .xlsx features, especially with recent Excel files.
# - Formatting, data validation, and advanced features may not be fully compared.
# - For .xlsx support, you may need to use xlrdiff with xlrd<=1.2.0 (not recommended for new projects).
# - This script mimics excel_compare.py structure, but uses xlrdiff for the actual comparison. 
from pathlib import Path
from arb.__get_logger import get_logger

__version__ = "1.0.0"

root_logger = file_path = Path(__file__).resolve().parents[3] / "logs"
logger, pp_log = get_logger(file_stem="arb_portal", file_path=root_logger, log_to_console=False)

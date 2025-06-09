from pathlib import Path

from arb.__get_logger import get_logger

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def extract_sector_payload(xl_dict: dict, metadata_key: str = "metadata", tab_name: str = "Feedback Form") -> dict:
  """
  Combines worksheet tab contents with sector metadata into a single payload for database insertion.

  Args:
      xl_dict (dict): Dictionary from an Excel-parsed source, containing 'metadata' and 'tab_contents'.
      metadata_key (str): Key in xl_dict containing the metadata dictionary (default: "metadata").
      tab_name (str): Name of the worksheet tab to extract from tab_contents (default: "Feedback Form").

  Returns:
      dict: Combined payload with tab_contents and sector included.

  Raises:
      ValueError: If the metadata key, sector, or tab_name is missing.
  """
  if metadata_key not in xl_dict:
    raise ValueError(f"Expected key '{metadata_key}' in xl_dict but it was missing.")

  metadata = xl_dict[metadata_key]
  sector = metadata.get("sector")
  if not sector:
    raise ValueError(f"Missing or empty 'sector' key in xl_dict['{metadata_key}'].")

  tab_contents = xl_dict.get("tab_contents", {})
  if tab_name not in tab_contents:
    raise ValueError(f"Tab '{tab_name}' not found in xl_dict['tab_contents'].")

  tab_data = tab_contents[tab_name].copy()
  tab_data["sector"] = sector
  return tab_data

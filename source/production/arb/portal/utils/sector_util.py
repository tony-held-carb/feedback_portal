"""
  Sector utilities for resolving and classifying feedback form sectors.

  This module provides functions to extract sector payloads from Excel data,
  resolve sector and sector_type for incidences, and map sector names to
  broad classifications (e.g., 'Oil & Gas', 'Landfill').

  Args:
    None

  Returns:
    None

  Attributes:
    extract_sector_payload (function): Combines worksheet tab and metadata into a payload.
    get_sector_info (function): Resolves sector and sector_type for an incidence ID.
    resolve_sector (function): Determines the correct sector from FK and JSON sources.
    get_sector_type (function): Maps a sector name to its broad classification.
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.utils.sector_util import get_sector_info
    sector, sector_type = get_sector_info(db, base, 123)

  Notes:
    - Used by feedback portal ingestion and display logic.
    - Integrates with SQLAlchemy and Excel ingestion utilities.
"""

import logging
from pathlib import Path
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase

from arb.portal.db_hardcoded import LANDFILL_SECTORS, OIL_AND_GAS_SECTORS
from arb.utils.sql_alchemy import get_foreign_value, get_table_row_and_column

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def extract_sector_payload(xl_dict: dict,
                           metadata_key: str = "metadata",
                           tab_name: str = "Feedback Form") -> dict:
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

  Examples:
    payload = extract_sector_payload(xl_dict)
    # Returns a dict with tab data and sector for database insertion

  Notes:
    - Used during Excel ingestion to prepare data for database upload.
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


def get_sector_info(db: SQLAlchemy,
                    base: AutomapBase,
                    id_: int) -> tuple[str, str]:
  """
  Resolve the sector and sector_type for a given incidence ID.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    base (AutomapBase): SQLAlchemy Automapped declarative base.
    id_ (int): ID of the row in the `incidences` table.

  Returns:
    tuple[str, str]: (sector, sector_type)

  Examples:
    sector, sector_type = get_sector_info(db, base, 123)
    # Returns the sector and its broad classification for the given ID

  Notes:
    - Uses both foreign key and misc_json to resolve the sector.
    - Returns the sector and its type for display or further processing.
  """
  logger.debug(f"get_sector_info() called to determine sector & sector type for {id_=}")
  primary_table_name = "incidences"
  json_column = "misc_json"

  # Find the sector from the foreign table if incidence was created by plume tracker.
  sector_by_foreign_key = get_foreign_value(
    db, base,
    primary_table_name=primary_table_name,
    foreign_table_name="sources",
    primary_table_fk_name="source_id",
    foreign_table_column_name="sector",
    primary_table_pk_value=id_,
  )

  # Get the row and misc_json field from the incidence table
  row, misc_json = get_table_row_and_column(
    db, base,
    table_name=primary_table_name,
    column_name=json_column,
    id_=id_,
  )

  if misc_json is None:
    misc_json = {}

  sector = resolve_sector(sector_by_foreign_key, row, misc_json)
  sector_type = get_sector_type(sector)

  logger.debug(f"get_sector_info() returning {sector=} {sector_type=}")
  return sector, sector_type


def resolve_sector(sector_by_foreign_key: str | None,
                   row: Any,
                   misc_json: dict) -> str:
  """
  Determine the appropriate sector from FK and JSON sources.

  Args:
    sector_by_foreign_key (str | None): Sector from `sources` table.
    row (Any): Row from `incidences` table (SQLAlchemy result).
    misc_json (dict): Parsed `misc_json` content.

  Returns:
    str: Sector string.

  Notes:
    - Prefers the sector from misc_json if both are present and conflict.
    - Logs warnings if sector cannot be determined.
    - Does not raise on mismatch, but logs an error.

  Examples:
    sector = resolve_sector('Oil', row, {'sector': 'Oil'})
    # Returns 'Oil' as the resolved sector
  """
  logger.debug(f"resolve_sector() called with {sector_by_foreign_key=}, {row=}, {misc_json=}")
  sector_by_json = misc_json.get("sector")

  if sector_by_foreign_key is None:
    logger.warning(f"sector column value in sources table is None.")

  if sector_by_json is None:
    logger.warning(f"'sector' not in misc_json")

  if sector_by_foreign_key is None and sector_by_json is None:
    logger.error(f"Can't determine incidence sector")
    raise ValueError("Can't determine incidence sector")

  if sector_by_foreign_key is not None and sector_by_json is not None:
    if sector_by_foreign_key != sector_by_json:
      logger.error(f"Sector mismatch: {sector_by_foreign_key=}, {sector_by_json=}")
      # raise ValueError("Can't determine incidence sector")

  # sector_by_json given priority over foreign key
  sector = sector_by_json or sector_by_foreign_key

  logger.debug(f"resolve_sector() returning {sector=}")
  return sector


def get_sector_type(sector: str) -> str:
  """
  Map a sector name to its broad classification.

  Args:
    sector (str): Input sector label.

  Returns:
    str: One of "Oil & Gas", "Landfill", or the original sector name for unsupported sectors.

  Notes:
    - For unsupported sectors, returns the original sector name so the calling code
      can handle it appropriately (e.g., show read-only view).
    - This prevents ValueError exceptions and allows graceful handling of new sectors.

  Examples:
    sector_type = get_sector_type('Oil & Gas')
    # Returns 'Oil & Gas'
    sector_type = get_sector_type('Unknown')
    # Returns 'Unknown' for unsupported sectors
  """

  if sector in OIL_AND_GAS_SECTORS:
    return "Oil & Gas"
  elif sector in LANDFILL_SECTORS:
    return "Landfill"
  else:
    # Return the original sector name for unsupported sectors
    # This allows the calling code to handle it gracefully
    return sector

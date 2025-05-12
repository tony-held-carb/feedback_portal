"""
Hardcoded test data and HTML selector utilities for the ARB operator portal.

This module provides:
    * Dummy payloads for Oil & Gas and Landfill sectors used in development/testing
    * Dropdown selector data for HTML forms
    * Example routines for injecting fake data into SQLAlchemy models

Notes:
    - All dates are generated dynamically using `datetime.datetime.now()`
    - Dropdown logic should be kept in sync with form validators and Excel schemas
"""

import datetime

import arb.__get_logger as get_logger
from arb.utils.web_html import update_selector_dict

logger, pp_log = get_logger.get_logger(__name__, __file__)


def add_og_dummy_data(db, base, table_name: str) -> None:
    """
    Inject dummy Oil & Gas data into the database for development or diagnostic purposes.

    This routine populates a specified SQLAlchemy table with a small number of dummy records
    using static offsets to avoid unique constraint violations. It is intended for local
    development and is not production-safe.

    Args:
        db: SQLAlchemy instance associated with the Flask app.
        base: DeclarativeMeta base for SQLAlchemy models.
        table_name: Name of the table to populate.

    Example:
        add_og_dummy_data(db, Base, "IncidenceTable")

    Warning:
        This function bypasses validation logic. Do not use in production.
    """
    from arb.utils.sql_alchemy import get_class_from_table_name

    logger.debug("Adding dummy Oil & Gas data to populate the database.")

    table = get_class_from_table_name(base, table_name)
    col_name = "misc_json"
    offset = 2_000_000  # avoid primary key conflict

    for i in range(1, 10):
        id_incidence = i + offset
        id_plume = i + 100
        lat_arb = i + 50.0
        long_arb = i + 75.0
        observation_timestamp = datetime.datetime.now()

        json_data = {
            "id_incidence": id_incidence,
            "id_plume": id_plume,
            "lat_arb": lat_arb,
            "long_arb": long_arb,
            "observation_timestamp": observation_timestamp,
            "facility_name": f"facility_{i}",
            "contact_name": f"contact_name_{i}",
            "contact_phone": f"(555) 555-5555x{i}",
            "contact_email": f"my_email_{i}@server.com",
            "sector": "Oil & Gas",
            "sector_type": "Oil & Gas",
        }

        model = table(description="Dummy data created by add_og_dummy_data",
                      **{col_name: json_data})

        logger.debug(f"Adding incidence with json dummy data: {json_data=}")
        db.session.add(model)

    db.session.commit()


def get_og_dummy_data() -> dict:
    """
    Generate a dummy payload resembling an Oil & Gas feedback report.

    Returns:
        dict: Structured JSON-like dictionary with sector-specific keys.

    Example:
        payload = get_og_dummy_data()
        print(payload["facility_name"])
    """
    return {
        "id_incidence": 1001,
        "id_plume": 1001,
        "observation_timestamp": datetime.datetime.now(),
        "lat_carb": 100.05,
        "long_carb": 100.06,
        "id_message": "id_message response",
        "facility_name": "facility_name response",
        "id_arb_eggrt": 1001,
        "contact_name": "contact_name response",
        "contact_phone": "(555) 555-5555",
        "contact_email": "my_email@email.com",
        "venting_exclusion": "Please Select",
        "venting_description_1": "venting_description_1 response",
        "ogi_performed": "Please Select",
        "ogi_date": datetime.datetime.now(),
        "ogi_result": "Please Select",
        "method21_performed": "Please Select",
        "method21_date": datetime.datetime.now(),
        "method21_result": "Please Select",
        "initial_leak_concentration": 1004,
        "venting_description_2": "venting_description_2 response",
        "initial_mitigation_plan": "initial_mitigation_plan response",
        "equipment_at_source": "Please Select",
        "equipment_other_description": "equipment_other_description response",
        "component_at_source": "Please Select",
        "component_other_description": "component_other_description response",
        "repair_timestamp": datetime.datetime.now(),
        "final_repair_concentration": 101.05,
        "repair_description": "repair_description response",
        "additional_notes": "additional_notes response",
        "sector": "Oil & Gas",
        "sector_type": "Oil & Gas",
    }


def get_landfill_dummy_data() -> dict:
    """
    Generate a dummy payload resembling a Landfill feedback report.

    Returns:
        dict: Structured JSON-like dictionary with sector-specific keys.
    """
    logger.debug("Generating dummy landfill data")

    return {
        "additional_activities": "additional_activities",
        "additional_notes": "additional_notes",
        "contact_email": "my_email@email.com",
        "contact_name": "contact_name",
        "contact_phone": "(555) 555-5555",
        "emission_cause": "Please Select",
        "emission_cause_notes": "emission_cause_notes",
        "emission_cause_secondary": "Please Select",
        "emission_cause_tertiary": "Please Select",
        "emission_identified_flag_fk": "Please Select",
        "emission_location": "Please Select",
        "emission_location_notes": "emission_location_notes",
        "emission_type_fk": "Please Select",
        "facility_name": "facility_name",
        "id_arb_swis": "id_arb_swis",
        # "id_incidence": 1003, # commented out so the primary key would be assigned by postgress
        "id_message": "id_message",
        "id_plume": 1002,
        "included_in_last_lmr": "Please Select",
        "included_in_last_lmr_description": "included_in_last_lmr_description",
        "initial_leak_concentration": 1002.5,
        "inspection_timestamp": datetime.datetime.now(),
        "instrument": "instrument",
        "last_component_leak_monitoring_timestamp": datetime.datetime.now(),
        "last_surface_monitoring_timestamp": datetime.datetime.now(),
        "lat_carb": 102.5,
        "lat_revised": 103.5,
        "long_carb": 104.5,
        "long_revised": 105.5,
        "mitigation_actions": "mitigation_actions",
        "mitigation_timestamp": datetime.datetime.now(),
        "observation_timestamp": datetime.datetime.now(),
        "planned_for_next_lmr": "Please Select",
        "planned_for_next_lmr_description": "planned_for_next_lmr_description",
        "re_monitored_concentration": 1002.5,
        "re_monitored_timestamp": datetime.datetime.now(),
        "sector": "Landfill",
        "sector_type": "Landfill",
    }


def get_excel_dropdown_data() -> tuple[dict, dict]:
    """
    Get dropdown option values used by both the HTML form and Excel templates.

    Returns:
        tuple[dict, dict]: A tuple containing two dictionaries:
            - First dictionary is flat options keyed by field name.
            - Second dictionary contains conditional options for dependent selectors.

    Example:
        dropdowns, contingent = get_excel_dropdown_data()
        options = dropdowns["ogi_result"]

    Notes:
        - All default fields include "Please Select" prepended.
        - Contingent dropdowns are not auto-prefixed.
        - TODO: Update frontend validation to reflect new dropdown dependencies.
    """
    # Flat (non-contingent) dropdowns for Oil & Gas and Landfill
    drop_downs = {
        "venting_exclusion": ["Yes", "No"],
        "ogi_performed": ["Yes", "No"],
        "ogi_result": [
            "Not applicable as OGI was not performed",
            "No source found",
            "Unintentional-leak",
            "Unintentional-non-component",
            "Venting-construction/maintenance",
            "Venting-routine",
        ],
        "method21_performed": ["Yes", "No"],
        "method21_result": [
            "Not applicable as Method 21 was not performed",
            "No source found",
            "Unintentional-below leak threshold",
            "Unintentional-leak",
            "Unintentional-non-component",
            "Venting-construction/maintenance",
            "Venting-routine",
        ],
        "equipment_at_source": [
            "Centrifugal Natural Gas Compressor",
            "Continuous High Bleed Natural Gas-actuated Pneumatic Device",
            "Continuous Low Bleed Natural Gas-actuated Pneumatic Device",
            "Intermittent Bleed Natural Gas-actuated Pneumatic Device",
            "Natural Gas-actuated Pneumatic Pump",
            "Pressure Separator",
            "Reciprocating Natural Gas Compressor",
            "Separator",
            "Tank",
            "Open Well Casing Vent",
            "Piping",
            "Well",
            "Other",
        ],
        "component_at_source": [
            "Valve",
            "Connector",
            "Flange",
            "Fitting - pressure meter/gauge",
            "Fitting - not pressure meter/gauge",
            "Open-ended line",
            "Plug",
            "Pressure relief device",
            "Stuffing box",
            "Other",
        ],
        "emission_identified_flag_fk": [
            "Operator was aware of the leak prior to receiving the CARB plume notification",
            "Operator detected a leak during follow-up monitoring after receipt of the CARB plume notification",
            "No leak was detected",
        ],
        "emission_type_fk": [
            "Not applicable as no leak was detected",
            "Operator was aware of the leak prior to receiving the notification, and/or repairs were in progress on the date of the plume observation",
            "An unintentional leak  (i.e., the operator was not aware of, and could be repaired if discovered)",
            "An intentional or allowable vent (i.e., the operator was aware of, and/or would not repair)",
            "Due to a temporary activity (i.e., would be resolved without corrective action when the activity is complete)",
        ],
        "emission_location": [
            "Not applicable as no leak was detected",
            "Gas Collection System Component (e.g., blower, well, valve, port)",
            "Gas Control Device/Control System Component",
            "Landfill Surface: Daily Cover",
            "Landfill Surface: Final Cover",
            "Landfill Surface: Intermediate Cover",
            "Leachate Management System",
            "Working Face (area where active filling was being conducted at the time of detection)",
        ],
        "emission_cause": [
            "Not applicable as no leak was detected",
            "Collection system downtime",
            "Construction - New Well Installation",
            "Construction - Well Raising or Horizontal Extension",
            "Cover integrity",
            "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
            "Cracked/Broken Seal",
            "Damaged component",
            "Insufficient vacuum",
            "Offline Gas Collection Well(s)",
            "Other",
            "Uncontrolled Area (no gas collection infrastructure)",
        ],
        "emission_cause_secondary": [
            "Not applicable as no leak was detected",
            "Not applicable as no additional leak cause suspected",
            "Collection system downtime",
            "Construction - New Well Installation",
            "Construction - Well Raising or Horizontal Extension",
            "Cover integrity",
            "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
            "Cracked/Broken Seal",
            "Damaged component",
            "Insufficient vacuum",
            "Offline Gas Collection Well(s)",
            "Other",
            "Uncontrolled Area (no gas collection infrastructure)",
        ],
        "emission_cause_tertiary": [
            "Not applicable as no leak was detected",
            "Not applicable as no additional leak cause suspected",
            "Collection system downtime",
            "Construction - New Well Installation",
            "Construction - Well Raising or Horizontal Extension",
            "Cover integrity",
            "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
            "Cracked/Broken Seal",
            "Damaged component",
            "Insufficient vacuum",
            "Offline Gas Collection Well(s)",
            "Other",
            "Uncontrolled Area (no gas collection infrastructure)",
        ],
        "included_in_last_lmr": ["Yes", "No"],
        "planned_for_next_lmr": ["Yes", "No"],
    }

    # keys to the contingent dropdowns follow the patter html_selector2_contingent_on_html_selector1
    # for instance, emission_cause_contingent_on_emission_location means that the choices for
    # emission_cause are based on a lookup of the value of emission_location

    drop_downs_contingent = {
        "emission_cause_contingent_on_emission_location": {
            "Gas Collection System Component (e.g., blower, well, valve, port)": [
                "Construction - New Well Installation",
                "Construction - Well Raising or Horizontal Extension",
                "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
                "Damaged component",
                "Insufficient vacuum",
                "Offline Gas Collection Well(s)",
                "Other",
            ],
            "Gas Control Device/Control System Component": [
                "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
                "Damaged component",
                "Other",
            ],
            "Landfill Surface: Daily Cover": [
                "Collection system downtime",
                "Construction - New Well Installation",
                "Construction - Well Raising or Horizontal Extension",
                "Cover integrity",
                "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
                "Cracked/Broken Seal",
                "Damaged component",
                "Insufficient vacuum",
                "Offline Gas Collection Well(s)",
                "Other",
                "Uncontrolled Area (no gas collection infrastructure)",
            ],
            "Landfill Surface: Intermediate Cover": [
                "Collection system downtime",
                "Construction - New Well Installation",
                "Cover integrity",
                "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
                "Cracked/Broken Seal",
                "Damaged component",
                "Insufficient vacuum",
                "Offline Gas Collection Well(s)",
                "Other",
                "Uncontrolled Area (no gas collection infrastructure)",
            ],
            "Landfill Surface: Final Cover": [
                "Collection system downtime",
                "Construction - New Well Installation",
                "Construction - Well Raising or Horizontal Extension",
                "Cover integrity",
                "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
                "Cracked/Broken Seal",
                "Damaged component",
                "Insufficient vacuum",
                "Offline Gas Collection Well(s)",
                "Other",
                "Uncontrolled Area (no gas collection infrastructure)",
            ],
            "Leachate Management System": [
                "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
                "Damaged component",
                "Offline Gas Collection Well(s)",
                "Other",
            ],
            "Working Face (area where active filling was being conducted at the time of detection)": [
                "Construction - New Well Installation",
                "Construction - Well Raising or Horizontal Extension",
                "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
                "Offline Gas Collection Well(s)",
                "Other",
                "Uncontrolled Area (no gas collection infrastructure)",
            ],
        }
    }

    # Note, the drop_downs get 'Please Select' prepended, but the drop_down_contingent content is not modified
    drop_downs = update_selector_dict(drop_downs)
    return drop_downs, drop_downs_contingent

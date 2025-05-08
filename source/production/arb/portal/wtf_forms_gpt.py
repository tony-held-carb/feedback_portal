"""
# todo - gpt did not seem to want to update the forms file, it said it was fine already
#        try again tomorrow, it may be tired tonight :)


Defines WTForms that can be used to simplify HTML form creation and validation
for the Oil & Gas and Landfill feedback workflows.

This module defines forms derived from FlaskForm. They are used in conjunction
with templates to render sector-specific feedback forms with conditional logic
and validators based on user inputs.

General-purpose WTForms utilities are located in:
    arb.utils.wtf_forms_util.py

Form classes:
    - OGFeedback: Oil & Gas sector form with conditional validation for venting,
      OGI/Method 21 logic, and equipment/component descriptions.
    - LandfillFeedback: Landfill sector form with contingent dropdowns, dynamic
      validation rules, and optional monitoring logic.

Each form includes:
    - Rich WTForms field definitions
    - Conditional validators depending on other fields
    - Custom validate() methods
    - Dynamic dropdown logic through determine_contingent_fields()

Example usage in Flask route:
    >>> form = OGFeedback()
    >>> if form.validate_on_submit():
    >>>     save_to_db(form.data)
"""

# [Imports and WTForms definitions omitted here — retained in full Canvas doc]


def run_diagnostics():
    """
    Run diagnostics on OGFeedback and LandfillFeedback forms.

    This function simulates common workflows and exercises dynamic logic,
    validators, and selector dependencies in both forms.

    Intended for development use only.

    Example:
        >>> if __name__ == "__main__":
        >>>     run_diagnostics()
    """
    from datetime import datetime

    def print_form_errors(form):
        for field in form:
            if field.errors:
                print(f"{field.name}: {field.errors}")

    print("\n[Running diagnostics for OGFeedback form...]")
    og_form = OGFeedback()
    og_form.id_incidence.data = 1
    og_form.id_plume.data = 2
    og_form.observation_timestamp.data = datetime.now()
    og_form.lat_carb.data = 36.77
    og_form.long_carb.data = -119.41
    og_form.facility_name.data = "Example Facility"
    og_form.contact_name.data = "John Smith"
    og_form.contact_phone.data = "(123) 456-7890"
    og_form.contact_email.data = "john@example.com"
    og_form.venting_exclusion.data = "Yes"
    og_form.venting_description_1.data = "Routine maintenance as allowed by section 95669.1(b)(1)."

    og_form.determine_contingent_fields()
    og_form.validate()
    print_form_errors(og_form)

    print("\n[Running diagnostics for LandfillFeedback form...]")
    lf_form = LandfillFeedback()
    lf_form.id_incidence.data = 10
    lf_form.id_plume.data = 11
    lf_form.observation_timestamp.data = datetime.now()
    lf_form.facility_name.data = "Sample Landfill"
    lf_form.contact_name.data = "Jane Doe"
    lf_form.contact_phone.data = "(321) 654-0987"
    lf_form.contact_email.data = "jane@landfill.org"
    lf_form.inspection_timestamp.data = datetime.now()
    lf_form.instrument.data = "TDL Analyzer"
    lf_form.emission_identified_flag_fk.data = "Operator detected a leak during follow-up monitoring after receipt of the CARB plume notification"
    lf_form.initial_leak_concentration.data = 1200
    lf_form.emission_type_fk.data = "An unintentional leak  (i.e., the operator was not aware of, and could be repaired if discovered)"
    lf_form.emission_location.data = "Gas Collection System Component (e.g., blower, well, valve, port)"
    lf_form.emission_cause.data = "Damaged component"
    lf_form.emission_cause_notes.data = "Cracked valve detected during routine inspection."
    lf_form.mitigation_actions.data = "Replaced faulty valve and resealed."
    lf_form.mitigation_timestamp.data = datetime.now()
    lf_form.re_monitored_concentration.data = 300
    lf_form.included_in_last_lmr.data = "Yes"
    lf_form.planned_for_next_lmr.data = "Yes"
    lf_form.last_surface_monitoring_timestamp.data = datetime.now()
    lf_form.last_component_leak_monitoring_timestamp.data = datetime.now()

    lf_form.determine_contingent_fields()
    lf_form.update_contingent_selectors()
    lf_form.validate()
    print_form_errors(lf_form)

    print("\n[Diagnostics complete.]")


if __name__ == "__main__":
    run_diagnostics()

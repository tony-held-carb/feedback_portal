Validation rules associated with operator feedback.
Updated: 05/15/25

- Field types are automatically enforced by WTForms, no need to check them.

A. Oil and Gas
----------------

1. Selector changes
   1.  Drop down choices do not change based on other drop down values - no need to check this feature

2. Contingent fields
   1. venting_exclusion_test = self.venting_exclusion.data == "Yes"
   2. ogi_test = self.ogi_performed.data == "Yes"
   3. method21_test = self.method21_performed.data == "Yes"
   4. self.ogi_result.data or self.method21_result.data in ["Venting-construction/maintenance", "Venting-routine"]
   5. self.ogi_result.data in self.unintentional_leak or self.method21_result.data in self.unintentional_leak:
   6. equipment_other_test = self.equipment_at_source.data == "Other"
   7. component_other_test = self.component_at_source.data == "Other"

3. Field level validation
   1. if self.observation_timestamp.data > self.ogi_date.data
   2. self.observation_timestamp.data > self.method21_date.data
   3. self.observation_timestamp.data > self.repair_timestamp.data
   4. if self.venting_exclusion.data == "Yes" and self.ogi_result.data in ["Unintentional-leak"]
   5. if self.venting_exclusion.data == "Yes" and self.method21_result.data in ["Unintentional-leak"]
   6. if self.ogi_result.data in self.unintentional_leak then self.method21_performed required
   7. ogi not performed, but ogi date or result provided
   8. method21 not performed, but method21 date or result provided
   9. self.ogi_performed.data == "Yes" but result is "not applicable because not performed"
   10. self.method21_performed.data == "Yes" but result is "not applicable because not performed"

B. Landfill
----------------

1. Selector changes
   1. self.emission_location.data should change the following drop down choices:
      1. self.emission_cause.choices
      2. self.emission_cause_secondary.choices
      3. self.emission_cause_tertiary.choices

2. Contingent fields
   1. emission_identified_test = self.emission_identified_flag_fk.data != "No leak was detected"
   2. lmr_included_test = self.included_in_last_lmr.data == "No"
   3. lmr_planned_test = self.planned_for_next_lmr.data == "No"

3. Field level validation
   1. if self.emission_identified_flag_fk.data == "No leak was detected":
      1. self.emission_type_fk
      2. self.emission_location
      3. self.emission_cause
      4. self.emission_cause_secondary
      5. self.emission_cause_tertiary
   2. elif self.emission_identified_flag_fk.data == "Operator was aware of the leak prior to receiving the CARB plume notification":
      1. self.emission_type_fk
   3. if self.emission_identified_flag_fk.data != "No leak was detected"
      1. self.emission_type_fk
      2. self.emission_location
      3. self.emission_cause
      4. self.emission_cause_secondary
      5. self.emission_cause_tertiary
   4. if self.inspection_timestamp.data and self.mitigation_timestamp.data:
      1. self.mitigation_timestamp
   5. self.emission_cause_secondary repeats self.emission_cause
   6. self.emission_cause_secondary repeats self.emission_cause or self.emission_cause_secondary


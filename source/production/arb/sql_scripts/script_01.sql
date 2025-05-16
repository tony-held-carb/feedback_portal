insert into sectors (description)
values ('Oil & Gas'),
       ('Livestock'),
       ('Landfills'),
       ('Anaerobic Digester'),
       ('Industrial - Other'),
       ('Compost'),
       ('Unknown');

insert into mitigation_types (description)
values ('Leak Stopped'),
       ('Undergoing Repairs'),
       ('Leak Repaired');

--emission_types primary keys are important as they are cited in literature.
--Do not change the primary key or description combinations.
insert into emission_types (id_type, description)
values (0, 'No response from operator'),
       (1, 'Process'),
       (2, 'Unintentional'),
       (3, 'Temporary'),
       (4, 'Not found');

insert into emission_identified_flags (id_flag, description)
values (0, 'No leak found'),
       (1, 'Leak found or already known to exist');

insert into inspection_flags (id_flag, description)
values (0, 'Operator did not perform an on-the-ground inspection'),
       (1, 'Operator performed on-the-ground inspection');

insert into incidence_qa_flags (id_flag, description)
values (0, 'Not appropriate to share with operator'),
       (1, 'Appropriate to share with operator');

insert into plume_qa_flags (id_flag, description)
values (0, 'Not Reviewed'),
       (1, 'Confirmed Likely'),
       (2, 'Suspect - Needs additional review'),
       (3, 'False Positive');

insert into emission_source_descriptions (description)
values ('Oil or gas production facility'),
       ('Gathering and boosting station'),
       ('Transmission compressor station'),
       ('Natural gas processing plant'),
       ('Natural gas storage facility'),
       ('Pipeline'),
       ('Other');

insert into equipment_type_descriptions (description)
values ('Tank'),
       ('Pressure separator'),
       ('Sump'),
       ('Pond'),
       ('Flare'),
       ('Reciprocating natural gas compressor'),
       ('Centrifugal natural gas compressor'),
       ('Continuous high bleed pneumatic device'),
       ('Continuous low bleed pneumatic device'),
       ('Intermittent bleed pneumatic device'),
       ('Pneumatic pump'),
       ('Open well casing vent'),
       ('Wellhead assembly'),
       ('Attached pipelines'),
       ('Other');

insert into component_leak_descriptions (description)
values ('Not applicable because there was no leak'),
       ('Connector'),
       ('Valve'),
       ('Flange'),
       ('Open-ended line'),
       ('Pressure/Vacuum relief valve'),
       ('Other');

insert into measurement_characterizations (description)
values ('Measurement was non-detect or below threshold'),
       ('An intentional or allowable vent (i.e., the operator was aware of, and/or would not repair)'),
       ('Due to a temporary activity (i.e., would be resolved without corrective action when the activity is complete)'),
       ('An unintentional leak (i.e., the operator was not aware of, and could be repaired if discovered)');

insert into measurement_units (description)
values ('ppmv'),
       ('ug/m^3');

-- drop-down options from quinn
insert into initial_inspections (description)
values ('Optical gas imaging'),
       ('Method 21');

insert into found_source_types (description)
values ('Venting'),
       ('Unintentional emission source (found with OGI)'),
       ('Leak (found with Method 21)'),
       ('No source found');

insert into survey_options (description)
values ('Method 21 measurement indicated a leak (for component sources)'),
       ('Method 21 measurement did not indicate a leak (for component sources)'),
       ('Not a "component" source, as defined in the Regulation');

insert into equipment_source (description)
values ('Centrifugal Natural Gas Compressor'),
       ('Continuous High Bleed Natural Gas-actuated Pneumatic Device'),
       ('Continuous Low Bleed Natural Gas-actuated Pneumatic Device'),
       ('Intermittent Bleed Natural Gas-actuated Pneumatic Device'),
       ('Natural Gas-actuated Pneumatic Pump'),
       ('Pressure Separator'),
       ('Reciprocating Natural Gas Compressor'),
       ('Separator'),
       ('Tank'),
       ('Open Well Casing Vent'),
       ('Piping'),
       ('Well'),
       ('Other');

insert into component_sources (description)
values ('Valve'),
       ('Connector'),
       ('Flange'),
       ('Fitting - pressure meter/gauge'),
       ('Fitting - not pressure meter/gauge'),
       ('Open-ended line'),
       ('Plug'),
       ('Pressure relief device'),
       ('Stuffing box'),
       ('Other');

insert into venting_exclusions (id_, description)
values (0, 'No'),
       (1, 'Yes');
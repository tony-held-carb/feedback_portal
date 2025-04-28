--drop SCHEMA IF EXISTS satellite_tracker_test;
--you may have to manual refresh then right-click delete satellite_tracker_test

CREATE SCHEMA IF NOT EXISTS satellite_tracker_test;

set
search_path to satellite_tracker_test, public;

CREATE TABLE sectors
(
    id_sector   serial4 PRIMARY KEY,
    description varchar NOT NULL
);

CREATE TABLE mitigation_types
(
    id_type     serial4 PRIMARY KEY,
    description varchar NOT NULL
);

CREATE TABLE emission_types
(
    id_type     serial4 PRIMARY KEY,
    description varchar NOT NULL
);

CREATE TABLE emission_identified_flags
(
    id_flag     serial4 PRIMARY KEY,
    description varchar NOT NULL
);

CREATE TABLE inspection_flags
(
    id_flag     serial4 PRIMARY KEY,
    description varchar NOT NULL
);

CREATE TABLE incidence_qa_flags
(
    id_flag     serial4 PRIMARY KEY,
    description varchar NOT NULL
);

CREATE TABLE plume_qa_flags
(
    id_flag     serial4 PRIMARY KEY,
    description varchar NOT NULL
);

CREATE TABLE plumes
(
    id_plume                  serial4 PRIMARY KEY,
    plume_name                varchar,
    plume_timestamp           timestamp,
    origin                    geometry(point, 4326),
    extent                    geometry(polygon, 4326),
    footprint                 geometry(polygon, 4326),
    emission_rate             float8,
    emission_rate_uncertainty float8,
    qa_comment                varchar,
    filepath                  varchar,
    import_timestamp          timestamp,
    plume_qa_flag_fk          integer REFERENCES plume_qa_flags (id_flag)
);

CREATE TABLE operators
(
    id_operator    serial4 PRIMARY KEY,
    operator_name  varchar,
    sector         varchar,
    operator_notes varchar
);

CREATE TABLE sources
(
    id_source         serial4 PRIMARY KEY,
    description       varchar,
    location          varchar,
    coordinates       geometry(point, 4326) NOT NULL,
    created_timestamp timestamp DEFAULT now(),
    created_by        varchar,
    sector_id_fk      integer REFERENCES sectors (id_sector),
    operator_id_fk    integer REFERENCES operators (id_operator)
);

CREATE TABLE incidences
(
    id_incidence                 serial4 PRIMARY KEY,
    description                  varchar,
    incidence_status             varchar,
    incidence_status_explanation varchar,
    notification_timestamp       timestamp,
    reply_timestamp              timestamp,
    inspection_timestamp         timestamp,
    identified_component         varchar,
    identified_component_notes   varchar,
    emission_type_notes          varchar,
    emission_location            varchar,
    emission_location_notes      varchar,
    emission_cause               varchar,
    emission_cause_notes         varchar,
    mitigated_flag               integer,
    mitigation_timestamp         timestamp,
    operator_comment             varchar,
    end_timestamp                timestamp,
    created_timestamp            timestamp DEFAULT now(),
    created_by                   varchar,
    source_id                    integer REFERENCES sources (id_source),
    incidence_qa_flag_fk         integer REFERENCES incidence_qa_flags (id_flag),
    inspection_flag_fk           integer REFERENCES inspection_flags (id_flag),
    emission_identified_flag_fk  integer REFERENCES emission_identified_flags (id_flag),
    emission_type_fk             integer REFERENCES emission_types (id_type),
    mitigation_type_fk           integer REFERENCES mitigation_types (id_type)
);

CREATE TABLE plume_incidence_mappings
(
    id_plume_fk        integer NOT NULL REFERENCES plumes (id_plume),
    id_incidence_fk    integer NOT NULL REFERENCES incidences (id_incidence),
    assigned_timestamp timestamp DEFAULT now(),
    assigned_by        varchar,
    incidence_comment  varchar,
    CONSTRAINT plume_incidence_mapping_pkey PRIMARY KEY (id_plume_fk, id_incidence_fk)
);

CREATE TABLE plume_source_mappings
(
    id_plume_fk        integer NOT NULL REFERENCES plumes (id_plume),
    id_source_fk       integer NOT NULL REFERENCES sources (id_source),
    assigned_timestamp timestamp DEFAULT now(),
    assigned_by        varchar,
    source_comment     varchar,
    CONSTRAINT plume_source_mapping_pkey PRIMARY KEY (id_plume_fk, id_source_fk)
);

CREATE TABLE operator_contacts
(
    id_contact     serial4 PRIMARY KEY,
    name           varchar,
    email          varchar,
    phone          varchar,
    contact_notes  varchar,
    operator_id_fk integer REFERENCES operators (id_operator),
    active         int
);

CREATE TABLE messages
(
    id_message serial4 PRIMARY KEY,
    content    JSON
);

insert into incidence_qa_flags (id_flag, description)
values (0, 'Not appropriate to share with operator'),
       (1, 'Appropriate to share with operator');

insert into plume_qa_flags (id_flag, description)
values (0, 'Not Reviewed'),
       (1, 'Confirmed Likely'),
       (2, 'Suspect - Needs additional review'),
       (3, 'False Positive');

insert into inspection_flags (id_flag, description)
values (0, 'Operator did not perform an on-the-ground inspection'),
       (1, 'Operator performed on-the-ground inspection');

insert into emission_identified_flags (id_flag, description)
values (0, 'No leak found'),
       (1, 'Leak found or already known to exist');

insert into emission_types (id_type, description)
values (0, 'No response from operator'),
       (1, 'Process'),
       (2, 'Unintentional'),
       (3, 'Temporary'),
       (4, 'Not found');

insert into mitigation_types (id_type, description)
values (0, 'Leak Stopped'),
       (1, 'Undergoing Repairs'),
       (2, 'Leak Repaired');

insert into sectors (id_sector, description)
values (0, 'Oil & Gas'),
       (1, 'Livestock'),
       (2, 'Landfills'),
       (3, 'Anaerobic Digester'),
       (4, 'Industrial - Other'),
       (5, 'Compost'),
       (6, 'Unknown');

-- added by tony 6/8/24
CREATE TABLE email_types
(
    id_type    serial4 PRIMARY KEY,
    email_type varchar NOT null,
    UNIQUE (email_type)
);

CREATE TABLE phone_types
(
    id_type    serial4 PRIMARY KEY,
    phone_type varchar NOT null,
    UNIQUE (phone_type)
);

CREATE TABLE orginizations
(
    id_org   serial4 PRIMARY KEY,
    org_name varchar NOT null,
    UNIQUE (org_name)
);


CREATE TABLE uuids_processed
(
    id uuid PRIMARY key
);

CREATE TABLE operator_contacts3
(
    id_contact      serial4 PRIMARY KEY,
    first_name      varchar,
    middle_names    varchar,
    last_name       varchar,
    prefix          varchar,
    suffix          varchar,
    title           varchar,
    contact_notes   varchar,
    active          int,
    orginization_fk integer REFERENCES orginizations (id_org)
);

insert into email_types (id_type, email_type)
values (0, 'Unspecified'),
       (1, 'Work'),
       (2, 'Personal'),
       (3, 'Other');

insert into phone_types (id_type, phone_type)
values (0, 'Unspecified'),
       (1, 'Work'),
       (2, 'Home'),
       (3, 'Cell'),
       (4, 'Other');

# Postgres Setup and Snapshot Restore Guide

This guide explains how to set up a local Postgres database for the feedback_portal project, including best practices for restoring from a snapshot and ensuring schema integrity.

---

## 1. Using a Local Postgres Database

Set your database URI as an environment variable (example):

```sh
export DATABASE_URI=postgresql+psycopg2://postgres:<your_password>@localhost:5432/tony_home_tracker
```

- Replace `<your_password>` with your actual Postgres password.
- The database name here is `tony_home_tracker`.

---

## 2. Creating and Restoring from a Snapshot

### **A. Drop and Recreate the Database**

If you want a clean slate (recommended for restoring a snapshot):

```sh
psql -U postgres -c "DROP DATABASE IF EXISTS tony_home_tracker;"
psql -U postgres -c "CREATE DATABASE tony_home_tracker;"
```

### **B. Ensure Required Roles and Extensions**

- If your snapshot references a custom role (e.g., `methane`), create it:
  ```sh
  psql -U postgres -c "CREATE ROLE methane LOGIN;"
  ```
- If your snapshot uses PostGIS types, enable the extension:
  ```sh
  psql -U postgres -d tony_home_tracker -c "CREATE EXTENSION postgis;"
  ```

### **C. Import the Snapshot**

Navigate to the directory containing your snapshot SQL file and run:

```sh
psql -U postgres -d tony_home_tracker -f current_satellite_tracker2507092101.sql > import.log 2>&1
```
- This will capture all output and errors in `import.log` for review.

### **D. Schema Considerations**
- The snapshot may create tables in a schema like `satellite_tracker_new`.
- Your SQLAlchemy config should set the search path accordingly:
  ```python
  'options': '-c search_path=satellite_tracker_new,public -c timezone=UTC'
  ```
- If you want all tables in `public`, you may need to edit the dump or use schema remapping.

---

## 3. Troubleshooting Common Issues

- **Role does not exist:** Create the missing role before import.
- **PostGIS types missing:** Install and enable PostGIS before import.
- **Primary keys/constraints missing:** Always restore into a fresh database. Check the dump for `ADD CONSTRAINT ... PRIMARY KEY` lines.
- **Schema mismatch:** Make sure your app's search path matches the schema in the dump.
- **Invalid command \N:** Usually caused by earlier errors; fix those and re-import.

---

## 4. Best Practices

- Always restore into a new, empty database to avoid conflicts.
- Review the import log for errors after every restore.
- Use DBeaver or `psql` to verify tables, constraints, and data.
- Set your `DATABASE_URI` and SQLAlchemy search path to match your schema.
- If you need to automate, use batch scripts and log all output for review.

---

## 5. Example: Automated Restore Script

```sh
psql -U postgres -c "DROP DATABASE IF EXISTS tony_home_tracker;"
psql -U postgres -c "CREATE DATABASE tony_home_tracker;"
psql -U postgres -c "CREATE ROLE methane LOGIN;"
psql -U postgres -d tony_home_tracker -c "CREATE EXTENSION postgis;"
psql -U postgres -d tony_home_tracker -f current_satellite_tracker2507092101.sql > import.log 2>&1
```

---

## 6. Reference Notes (from notes.txt)

```
using a local postgres database
  export DATABASE_URI=postgresql+psycopg2://postgres:<your_password>@localhost:5432/tony_home_tracker
```

```
while [ 1 ]
do
  env LD_LIBRARY_PATH=/home/plumes/apps/builds/postgresql-16.1/src/interfaces/libpq /home/plumes/apps/builds/postgresql-16.1/src/bin/pg_dump/pg_dump  --schema=satellite_tracker_new -d postgres://methane:methaneCH4@prj-bus-methane-aurora-postgresql-instance-1.cdae8kkz3fpi.us-west-2.rds.amazonaws.com:5432/plumetracker | gzip | aws s3 cp - s3://carbmethane/backups/plume_tracker_db/current_satellite_tracker`date +%y%m%d%H%M`.sql.gz
  sleep 3600
done
```

- The above script shows how the production snapshot is created (hourly, from the remote Aurora instance, for the `satellite_tracker_new` schema).

---

*Last updated: 2025-07-10* 
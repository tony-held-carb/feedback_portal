# Exporting All Tables in the `satellite_tracker_new` Schema Using DBeaver

This guide provides a step-by-step checklist for exporting all tables in the `satellite_tracker_new` schema from your PostgreSQL database using the latest version of DBeaver.

---

## 1. Open DBeaver and Connect to Your Database
- Launch DBeaver.
- Connect to your `plumetracker` database.

## 2. Locate the Schema
- In the **Database Navigator** panel, expand:
  - Your connection → `plumetracker` → **Schemas** → `satellite_tracker_new`.

## 3. Open the Data Export Wizard
- Right-click on the **Tables** node under `satellite_tracker_new`.
  - (If you don’t see a “Tables” node, right-click the schema name itself.)
- Select **Tools → Data Export**.

## 4. Select Tables to Export
- In the export wizard, you should see a list of all tables in `satellite_tracker_new`.
- **Check the box at the top** to select all tables, or manually check each table you want to export.

## 5. Choose Export Format
- Under **Format**, select:
  - **SQL** (for a SQL dump with CREATE TABLE and INSERT statements)
  - Or **CSV** (if you want CSVs for each table; not recommended for schema migration)
- For most use cases, **SQL** is preferred.

## 6. Configure Export Options
- **Data**: Check “Export Data” to include table data (INSERTs).
- **DDL**: Check “Export DDL” to include table structure (CREATE TABLE).
- **Output**: Choose “Single file” and specify the output file path (e.g., `satellite_tracker_new_full.sql`).
- **Encoding**: Use UTF-8 (default).

## 7. Advanced Options (Optional)
- You can adjust options for:
  - Including/excluding indexes, constraints, triggers, etc.
  - Disabling “DROP TABLE” if you don’t want destructive statements.
- For SQLite conversion, you may want to:
  - Use “INSERT” statements (not “COPY”)
  - Avoid Postgres-specific types if possible

## 8. Start the Export
- Click **Start** (or **Next** then **Finish**) to begin the export.
- Wait for the process to complete. The progress bar will show export status.

## 9. Verify the Output
- Open the resulting `.sql` file in a text editor.
- Confirm that it contains:
  - `CREATE TABLE` statements for all tables in `satellite_tracker_new`
  - `INSERT INTO` statements with data for each table

## 10. Transfer the File
- Move the `.sql` file to your desired location (e.g., your home computer for SQLite conversion).

---

## Quick Checklist

- [ ] Open DBeaver and connect to `plumetracker`
- [ ] Expand Schemas → `satellite_tracker_new` → Tables
- [ ] Right-click **Tables** → Tools → Data Export
- [ ] Select **all tables** in the schema
- [ ] Choose **SQL** as the format
- [ ] Check “Export Data” and “Export DDL”
- [ ] Set output file and encoding
- [ ] Start export and wait for completion
- [ ] Verify `.sql` file contains all tables and data

---

**Tip:**
If you want to export all schemas, repeat the process at the database level or select multiple schemas/tables as needed.

If you need a screenshot-based guide or have trouble with any step, let me know! 
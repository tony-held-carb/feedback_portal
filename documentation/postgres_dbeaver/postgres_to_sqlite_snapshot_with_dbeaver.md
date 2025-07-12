# Creating a Postgres-to-SQLite Snapshot Using DBeaver

This guide explains how to use DBeaver to export your PostgreSQL database and convert it to a SQLite snapshot for local integration testing.

---

## 1. Export Data from PostgreSQL in DBeaver

### Option A: Export as SQL INSERT Statements
1. **Connect to your Postgres database** in DBeaver.
2. **Right-click the database or schema** you want to export.
3. Select **Tools → Data Export**.
4. In the export wizard:
   - **Select the tables** you want to export.
   - **Choose “Database” as the output format** (not “CSV”).
   - **Set “Export Data” to “SQL INSERTs”** (not “COPY” or “Native”).
   - Choose to export schema and/or data as needed.
   - Set the output file (e.g., `db_dump.sql`).
5. Click **Start** to export.

### Option B: Export as CSV Files (for each table)
1. Right-click a table → **Export Data**.
2. Choose **CSV** as the format.
3. Repeat for each table you need.

---

## 2. Convert the Exported Data to SQLite

### If you exported as SQL INSERTs:
- Use a tool like [`pg2sqlite`](https://github.com/dumblob/pg2sqlite) or [`sqlite3`](https://www.sqlite.org/cli.html) to import the SQL into SQLite.
  - Example: `pg2sqlite db_dump.sql arb_test_snapshot.sqlite`

### If you exported as CSVs:
- Use the SQLite CLI or a tool like [`sqlite-utils`](https://sqlite-utils.datasette.io/en/stable/cli.html#importing-csv-files) to import each CSV into a new SQLite database.

---

## 3. Bring the SQLite File Home
- Copy the resulting `arb_test_snapshot.sqlite` file to your home computer.
- Set your test config to use:
  ```
  SQLALCHEMY_DATABASE_URI = 'sqlite:///arb_test_snapshot.sqlite'
  ```

---

## Tips for DBeaver Export
- **Exporting schema:** If you want to preserve table structure, make sure to export both schema and data.
- **Data types:** Some Postgres types may not map perfectly to SQLite. You may need to tweak the SQL or use a conversion tool.
- **Foreign keys and constraints:** SQLite is less strict than Postgres; some constraints may be ignored or need manual adjustment.

---

## Summary Table

| Step                | In DBeaver? | Tool/Action                                  |
|---------------------|-------------|----------------------------------------------|
| Export as SQL       | Yes         | Data Export → SQL INSERTs                    |
| Export as CSV       | Yes         | Data Export → CSV (per table)                |
| Convert to SQLite   | No          | Use `pg2sqlite` or SQLite CLI                |
| Use in tests        | N/A         | Set `SQLALCHEMY_DATABASE_URI` to SQLite file |

---

## If You Need a Script
- If you want to automate the import of CSVs into SQLite, you can use Python or shell scripts. Ask for a sample if needed. 
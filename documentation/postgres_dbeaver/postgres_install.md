# PostgreSQL/PostGIS Home Installation Guide

**Work machine PostgreSQL version:**

    PostgreSQL 14.6 on x86_64-pc-linux-gnu, compiled by x86_64-pc-linux-gnu-gcc (GCC) 7.4.0, 64-bit

**Home machine (Windows) system information:**

- Host Name: TONY_DESKTOP
- OS Name: Microsoft Windows 11 Home
- OS Version: 10.0.26100 N/A Build 26100
- System Manufacturer: Gigabyte Technology Co., Ltd.
- System Model: B660 DS3H AC DDR4-Y1
- System Type: x64-based PC
- Processor: Intel64 Family 6 Model 183 Stepping 1 GenuineIntel ~2100 MHz
- Total Physical Memory: 130,905 MB (128 GB)
- Available Physical Memory: 110,802 MB
- Time Zone: (UTC-08:00) Pacific Time (US & Canada)
- Network: Realtek PCIe GbE, Realtek 8821CE Wireless LAN 802.11ac PCI-E NIC
- **PostgreSQL version installed:** postgresql-14.18-2-windows-x64.exe (closest available to 14.6, per assistant
  recommendation)

This guide helps you mirror your work PostgreSQL (with PostGIS) setup on your home Windows machine, ensuring geospatial
and other capabilities match as closely as possible.

---

## Connecting to PostgreSQL with pgAdmin

When registering a new server in pgAdmin to connect to your local PostgreSQL instance, you **must** enter `localhost` (
or `127.0.0.1`) in the **Host name/address** field on the Connection tab. If you leave this field blank, pgAdmin will
not be able to connect and will display an error ("Either Host name or Service must be specified").

- Host name/address: `localhost`
- Port: `5432` (default)
- Maintenance database: `postgres`
- Username: `postgres` (or your superuser name)
- Password: (the one you set during install)

This is required for local connections, even if PostgreSQL is running on the same machine as pgAdmin.

---

## Note on the "Create spatial database" Option in the PostGIS Installer

During the PostGIS Bundle installation, you may see an option labeled **"Create spatial database"**. Here’s what it
means and the consequences of selecting or not selecting it:

- **If you select this option:**
    - The installer will prompt you for database connection details (host, port, user, password).
    - It will automatically create a new PostgreSQL database (often named `postgis` or a name you specify).
    - It will initialize this database with the PostGIS extension (and possibly other spatial extensions), so it’s ready
      for spatial/GIS work immediately.

- **If you do NOT select this option:**
    - No new database will be created during installation.
    - You will need to manually create any databases you want and enable PostGIS in them using:
      ```sql
      CREATE EXTENSION postgis;
      ```

- **Recommendation:**
    - Most users leave this unchecked and manually enable PostGIS in whichever databases they want later.
    - If you want a quick start or a sample spatial database, you can check it and let the installer create one for you.

- **Summary:**
    - “Create spatial database” = automatic creation and initialization of a new PostGIS-enabled database during
      install.
    - You can always create and enable PostGIS in any database later using the SQL command above.

---

## 1. Match PostgreSQL Version

- **Check work version:**
  ```sql
  SELECT version();
  ```
- **Install the same version** on your home
  machine ([Download PostgreSQL 14.6 for Windows](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)).

---

## 2. Install PostGIS Extension

- Use **Stack Builder** after installing PostgreSQL.
- Under **Spatial Extensions**, select:
    - **PostGIS 3.4 Bundle for PostgreSQL 14** (for best compatibility with work's PostGIS 3.2.3).
- Proceed with the installation.

---

## 3. Enable Extensions in Your Database

After installation, for each database where you need GIS/table functions:

```sql
CREATE EXTENSION postgis;
CREATE EXTENSION tablefunc;
```

- For topology or raster support (optional):
  ```sql
  CREATE EXTENSION postgis_topology;
  CREATE EXTENSION postgis_raster;
  ```

---

## 4. Verify Installation

Run these queries to confirm everything is working:

```sql
SELECT PostGIS_Version();
SELECT * FROM pg_extension;
```

- You should see `postgis` and `tablefunc` in the results.

---

## 5. (Optional) Match Locale, Encoding, and Timezone

To match your work environment exactly:

```sql
SHOW lc_collate;
SHOW lc_ctype;
SHOW server_encoding;
SHOW timezone;
```

- If you need to change these, do so when creating a new database.

---

## 6. (Optional) Restore Schema/Data

If you want to copy tables, roles, or data from work:

- On work:
  ```sh
  pg_dump -s -U youruser -d yourdb > schema.sql
  pg_dump -a -U youruser -d yourdb > data.sql
  ```
- On home:
  ```sh
  psql -U youruser -d yourdb -f schema.sql
  psql -U youruser -d yourdb -f data.sql
  ```

---

## 7. After-Install Checklist

| Step                           | Command/Action                                                |
|--------------------------------|---------------------------------------------------------------|
| Restart PostgreSQL (if needed) | Use Windows Services or installer prompt                      |
| Connect to DB                  | psql/pgAdmin                                                  |
| Enable PostGIS                 | `CREATE EXTENSION postgis;`                                   |
| Enable tablefunc               | `CREATE EXTENSION tablefunc;`                                 |
| (Optional) Enable topology     | `CREATE EXTENSION postgis_topology;`                          |
| (Optional) Enable raster       | `CREATE EXTENSION postgis_raster;`                            |
| Verify                         | `SELECT PostGIS_Version();` and `SELECT * FROM pg_extension;` |
| (Optional) Match locale/etc    | `SHOW lc_collate;` etc.                                       |
| (Optional) Restore schema      | Use `pg_dump`/`psql`/`pg_restore`                             |

---

## 8. Troubleshooting

- If you don't see PostGIS in Stack Builder, ensure you selected your PostgreSQL 14 instance at the start.
- `tablefunc` is not in Stack Builder; it is included with PostgreSQL and enabled via SQL.
- For more extensions, repeat the process as needed.

---

**You’re ready!**
Just follow these steps after the install and you’ll have a home PostgreSQL setup that closely matches your work
environment.

---

**Appendix: Work Machine Extension List**

Below is the list of extensions installed on the work machine, as shown by `SELECT * FROM pg_extension`:

| oid      | extname   | extowner | extnamespace | extrelocatable | extversion | extconfig  | extcondition  |
|----------|-----------|----------|--------------|----------------|------------|------------|---------------|
| 14703    | plpgsql   | 10       | 11           | FALSE          | 1          |            |               |
| 20979882 | postgis   | 10       | 2200         | FALSE          | 3.2.3      | {20980193} | {"WHERE ..."} |
| 22461892 | tablefunc | 16587    | 22409454     | TRUE           | 1          |            |               |

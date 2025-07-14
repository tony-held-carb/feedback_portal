@main.route("/test_spinner", methods=["GET", "POST"])
def test_spinner():
  if request.method == "POST":
    file = request.files.get("file")
    if file:
      import time
      time.sleep(2)  # simulate processing delay
      flash(f"File '{file.filename}' uploaded successfully.", "success")
    return redirect(url_for("main.test_spinner"))

  return render_template("test_spinner.html")

@main.route('/modify_json_content')
def modify_json_content():
  """
  Flask route to demonstrate how to update a json field in a postgres column.

  Notes:
    - Depreciated and only kept for diagnostics, don't use in production.
    - ORM can get confused if you modify the json leading to it not being persisted properly:
      https://bashelton.com/2014/03/updating-postgresql-json-fields-via-sqlalchemy/
  """
  base: DeclarativeMeta = current_app.base  # type: ignore[attr-defined]

  id_incidence = 5  # hard coded incidence to modify

  # for i, map_name in enumerate(Base.classes):
  #   table_name = str(map_name.__table__.name)
  #   print(i, table_name)
  incidences = base.classes.incidences

  session = db.session
  model = session.query(incidences).get(id_incidence)
  logger.debug(f"{model=}")
  json_content = model.misc_json

  time_stamp = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S")
  json_content['time_stamp'] = time_stamp

  model.misc_json = json_content
  flag_modified(model, "misc_json")
  # model.misc_json['temp'] = 123456
  db.session.add(model)
  db.session.commit()

  return json_content

@main.route('/run_sql_script')
def run_sql_script():
  """
 (Outdated) Flask route to run a sql_script which adds tables & data to the database from a
  sql text file and convert some tables into drop-down structures suitable for select drop-downs.
  """
  return "This script is no longer in service - it was originally designed for sqlite"
  # logger.info(f"Running sql script")
  # database.add_static_table_content()
  # # update drop-down tables
  # Globals.load_drop_downs(app)
  # return '<h1>SQL script run</h1>'

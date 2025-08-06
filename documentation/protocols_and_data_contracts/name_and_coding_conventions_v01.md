# Naming and code conventions for the portal

SQLAlchemy Naming Conventions
---------------------

* pass an sql model as model_rows and iterate through it with for model_row in model_rows
* Use model_row if you have a single row from a query
* don't use form as a variable in html, it is confusing. if you want to pass a WTForm, use the variable wtf_form

Datetime string conventions
---------------------------

- When you create an SQLAlchemy model, you can use a dict to represent the json column
- That dict can contain any python types, but if you try to write the json to the database, the type must serialize as a
  string
- datetimes coming into and out of the postgres database should follow the format "2024-09-03 16:55:00.000000"
  - logger.debug(f"Attempting to cast datetime to string")
  - value = datetime.datetime.strftime(value, "%Y-%m-%d %H:%M:%S.%f")
  - if isinstance(obj, datetime):
  return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
  value = datetime.datetime.strftime(value, "%Y-%m-%d %H:%M:%S.%f")

Quotations
---------------------------

- When using quotes, for example in a spreadsheet label, use single quotes ', not double quotes "
- This avoids some issues when converting strings to json
- In python coding, use double quotes to wrap strings when possible, that way single quotes can still be embedded
- I commonly use single quotes for dictionary keys and I'm not sure it makes sense to standardize all usage

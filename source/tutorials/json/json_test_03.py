import json
from datetime import datetime


class CustomEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime):
      return {"__type__": "datetime", "value": obj.isoformat()}
    return super().default(obj)


data = {"date": datetime.now()}
json_str = json.dumps(data, cls=CustomEncoder)
print(json_str)

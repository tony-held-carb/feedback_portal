import json
from datetime import datetime


# Custom encoder
class CustomEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime):
      return {"__type__": "datetime", "value": obj.isoformat()}
    return super().default(obj)


# Custom decoder
def custom_decoder(obj):
  if "__type__" in obj and obj["__type__"] == "datetime":
    return datetime.fromisoformat(obj["value"])
  return obj


# Example usage
data = {"name": "myname", "date": datetime.now()}

json_str = json.dumps(data, cls=CustomEncoder)
print("Serialized:", json_str)

# Deserialize
decoded_data = json.loads(json_str, object_hook=custom_decoder)
print("Deserialized:", decoded_data)
print("Type of 'date':", type(decoded_data["date"]))

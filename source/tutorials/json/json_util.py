"""
Template to demonstrate how to serialize and deserialize JSON data for custom datatypes (such as datetime)
"""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class Address:
  def __init__(self, street, city, state, zip):
    self.street = street
    self.city = city
    self.state = state
    self.zip = zip

  def __repr__(self):
    return f"Address(street={self.street}, city={self.city}, state={self.state}, zip={self.zip})"


class User:
  def __init__(self, name, age, address):
    self.name = name
    self.age = age
    self.address = address
    self.created_local = datetime.now()
    self.created_utc = datetime.now(timezone.utc)

  def __repr__(self):
    return (f"User(name={self.name}, age={self.age}, address={self.address}, "
            f"created_local={self.created_local}, created_utc={self.created_utc}, )")


def serializer(obj):
  """
  Custom JSON serializer for objects not serializable by default
  """
  logger.debug(f"custom_serializer() called with type= {type(obj)}, obj={obj}")
  if isinstance(obj, datetime):
    return {"__type__": "datetime", "value": obj.isoformat()}
  elif isinstance(obj, Address):
    return \
      {"__type__": "Address",
       "value":
         {'street': obj.street,
          'city': obj.city,
          'state': obj.state,
          'zip': obj.zip
          }
       }
  elif isinstance(obj, User):
    return \
      {"__type__": "User",
       "value":
         {"name": obj.name,
          "age": obj.age,
          "address": obj.address,
          "created_local": obj.created_local,
          "created_utc": obj.created_utc,
          }
       }
  raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def deserializer(obj):
  logger.debug(f"deserializer() called with type= {type(obj)}, obj={obj}")

  new_obj = obj

  if "__type__" in obj:
    logger.debug(f'{obj["__type__"]=} detected in object deserializer.')
    if obj["__type__"] == "datetime":
      new_obj = datetime.fromisoformat(obj["value"])
    elif obj["__type__"] == "User":
      value = obj["value"]
      new_obj = User(value['name'], value['age'], value['address'])
      new_obj.created_local = value['created_local']
      new_obj.created_utc = value['created_utc']
    elif obj["__type__"] == "Address":
      value = obj["value"]
      new_obj = Address(value['street'], value['city'], value['state'], value['zip'])
    else:
      logger.debug(f'No known conversion type for type {obj["__type__"]}')

    logger.debug(f"deserializer() returning type= {type(new_obj)}, new_obj= {new_obj}")

  return new_obj


def get_example_data():
  logger.debug(f"Creating example data for json testing")

  address_01 = Address("1 Main Street", "Sacramento", "CA", "95817")
  address_02 = Address("2 Second Street", "Sacramento", "CA", "95819")
  logger.debug(f"{address_01= }")
  logger.debug(f"{address_02= }")

  user_01 = User("George", "Harrison", address_01)
  user_02 = User("Ringo", "Starr", address_02)
  logger.debug(f"{user_01= }")
  logger.debug(f"{user_02= }")

  data_list = [address_01, address_02, user_01, user_02]
  data_dict = {'key_01': address_01, 'key_02': address_02, 'key_03': user_01, 'key_04': user_02}

  return data_list, data_dict


def json_dump(data, comment=None, serializer=None):
  if comment:
    logger.debug(f"{comment}\n")

  logger.debug(f"Serializing python list to json str.  \n\t{data= }")
  json_str = json.dumps(data, default=serializer, )
  logger.debug(f"\n\t{json_str=  }")
  return json_str


def json_load(json_str, comment=None, deserializer=None):
  if comment:
    logger.debug(f"{comment}\n")

  logger.debug(f"Deserializing json str to python variable.  \n\t{json_str= }")
  decoded_data = json.loads(json_str, object_hook=deserializer)
  logger.debug(f"\n\t{decoded_data=  }")
  return decoded_data


if __name__ == "__main__":
  logging.basicConfig(filename='json.log',
                      level=logging.DEBUG,
                      format='+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(filename)s | %(lineno)d | %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S',
                      )

  data_list, data_dict = get_example_data()
  # Serialize
  json_str = json_dump(data_list, serializer=serializer, comment='Array of multiple class types')
  # Deserialize
  decoded_data = json_load(json_str, deserializer=deserializer,
                           comment='Extracting custom classes (including local and utc datetimes)')

  # Scratch code below
  # --------------------
  # simple_list = ["one", "two", "three", 4]
  # simple_dict = {"one": 1, 2: "two", "three": 3, 4: 4}

  # json_str = json_dump_01(simple_list, comment='Simple list, no serialization')
  # json_str = json_dump_01(simple_dict, comment='Simple dict, no serialization')

  # next line will fail without custom serializer
  # json_dump_no_serialization_01(data_list, 'Data with user defined classes')

  # json_str = json_dump_01(data_list[0], comment='Single obj of Address class', serializer=custom_serializer)
  # json_str = json_dump_01(data_list[3], comment='Single obj of User class', serializer=custom_serializer)
  # json_str = json_dump(data_list, comment='Array of multiple classes', serializer=custom_serializer)
  # json_str = json_dump_01(data_dict, comment='Dict of multiple classes', serializer=custom_serializer)

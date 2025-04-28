import json
import pprint

from pprint import pprint


def read_json_file_01(file_name: str):
  print(f"\nReading file: {file_name}")
  with open(file_name, 'r') as file:
    data = json.load(file)

  print(f"{type(data)=}")
  # Print the data
  pprint(data)
  return data


def write_json_file_01(data, file_name: str = "json_out.json", **kwargs):
  print(f"\nWriting file: {file_name}")
  print(f"{type(data)=}")
  pprint(data)

  with open(file_name, 'w') as file:
    json.dump(data, file, **kwargs)


def example_01(file_name="example_01.json"):
  food_ratings = {"organic dog food": 2, "human food": 10}
  write_json_file_01(food_ratings, file_name=file_name)


def example_02(file_name="example_02.json"):
  my_dict = {1: 2, 3: 4}
  write_json_file_01(my_dict, file_name=file_name)


def example_03(file_name="example_03.json"):
  my_array = [1, 2, 3, 4.0]
  write_json_file_01(my_array, file_name=file_name, indent=2)


if __name__ == '__main__':
  data = read_json_file_01(file_name='hello_frieda_01.json')
  write_json_file_01(data, file_name='hello_frieda_01_out.json')
  write_json_file_01(data, file_name='hello_frieda_01_out.json', indent=2)
  # read_json_file_01(file_name='hello_frieda_02.json')
  # example_01()
  # example_02()
  # example_03()
  # read_json_file_01(file_name="example_01.json")
  # read_json_file_01(file_name="example_01.json")
  # read_json_file_01(file_name="example_02.json")
  # read_json_file_01(file_name="example_03.json")

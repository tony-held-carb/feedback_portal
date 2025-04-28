import json
from datetime import datetime


def json_save_with_meta(file_path, data, meta_data=None, json_options=None):
  """
  Save a data object to a JSON file with metadata such as save time and notes.

  Args:
      file_path (str): Path to the JSON file.
      data: The data to save.
      meta_data (dict): meta_data describing the data.
      json_options (dict): JSON options to include with dump function.
  """
  if meta_data is None:
    meta_data = {"saved_at": datetime.now().isoformat(), 'created_with': "json_save_with_meta function"}

  if json_options is None:
    json_options = {'indent': 4}

  # Add meta information to the data
  data_with_meta = {
    "_meta_data_": meta_data,
    "data": data
  }

  # Write to JSON file
  with open(file_path, 'w') as f:
    json.dump(data_with_meta, f, **json_options)
  print(f"Data saved with metadata to '{file_path}'.")


def json_load_with_meta(file_path, json_options=None):
  """
  Load a JSON file separating returning the data and metadata as separate variables.

  Args:
      file_path (str): Path to the JSON file.
      json_options (dict | None): Options passed to the `json.load` function.

  Returns:
      tuple[dict, dict]: A tuple containing:
          - data (dict): The deserialized JSON data without metadata.
          - meta_data (dict): The deserialized JSON metadata.
  """
  if json_options is None:
    json_options = {}

  # Read JSON file
  with open(file_path, 'r') as f:
    data_with_meta = json.load(f, **json_options)

  # Get the data and meta_data separately
  data = data_with_meta.get("data", {})
  meta_data = data_with_meta.get("_meta_data_", {})

  return data, meta_data


# Example Usage
if __name__ == "__main__":
  # Example data
  sample_data = {
    "name": "Alice",
    "age": 30,
    "city": "Wonderland"
  }

  # File path
  json_file = "example_data.json"

  # Save with metadata
  json_save_with_meta(json_file, sample_data, )

  # load with metadata
  data, meta_data = json_load_with_meta(json_file)
  print(f"{data=}")
  print(f"{meta_data=}")

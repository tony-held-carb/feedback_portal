import json
from datetime import datetime


def save_with_meta(data, file_path, notes=""):
  """
  Save a dictionary to a JSON file with metadata such as save time and notes.

  Args:
      data (dict): The data to save.
      file_path (str): Path to the JSON file.
      notes (str): Optional notes to include in the metadata.
  """
  # Add meta information to the data
  data_with_meta = {
    "_meta": {
      "notes": notes,
      "saved_at": datetime.now().isoformat()
    },
    "data": data
  }

  # Write to JSON file
  with open(file_path, 'w') as f:
    json.dump(data_with_meta, f, indent=4)
  print(f"Data saved with metadata to '{file_path}'.")


def load_stripped_json(file_path):
  """
  Load a JSON file and return only the user data, stripping out metadata.

  Args:
      file_path (str): Path to the JSON file.

  Returns:
      dict: The deserialized data without metadata.
  """
  # Read JSON file
  with open(file_path, 'r') as f:
    data_with_meta = json.load(f)

  # Strip out meta information
  user_data = data_with_meta.get("data", {})
  print("Metadata stripped out during deserialization.")
  return user_data


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
  save_with_meta(sample_data, json_file, notes="This file contains sample user data.")

  # Load and strip metadata
  clean_data = load_stripped_json(json_file)
  print("Deserialized Data (without meta):")
  print(clean_data)

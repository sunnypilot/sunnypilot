import requests
import hashlib
import json

# Function to calculate SHA-256 hash of a file downloaded from a given URI
def calculate_hash(download_uri):
  response = requests.get(download_uri, stream=True)
  hash_sha256 = hashlib.sha256()
  for chunk in response.iter_content(chunk_size=1024):
    hash_sha256.update(chunk)
  return hash_sha256.hexdigest()

# Download the models_v3.json file
models_v3_url = "https://docs.sunnypilot.ai/models_v3.json"
response = requests.get(models_v3_url)
models_data = response.json()

# Iterate through each model and calculate SHA-256 for its files
for model_key, model_info in models_data.items():
  # Calculate and insert the SHA-256 hash for each download URI
  model_info['download_uri'] = {'url': model_info['download_uri'], 'sha256': calculate_hash(model_info['download_uri'])}
  model_info['download_uri_nav'] = {'url': model_info['download_uri_nav'], 'sha256': calculate_hash(model_info['download_uri_nav'])}
  model_info['download_uri_metadata'] = {'url': model_info['download_uri_metadata'], 'sha256': calculate_hash(model_info['download_uri_metadata'])}

# Save the updated JSON with hashes
updated_json_file_path = 'updated_models_v3.json'  # Path for the updated JSON file
with open(updated_json_file_path, 'w') as file:
  json.dump(models_data, file, indent=4)

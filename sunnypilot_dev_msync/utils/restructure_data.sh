#!/bin/bash


# Set this to your Chunk directory
CHUNK_DIR="comma2k19/Chunk_1"

cd "$CHUNK_DIR" || { echo "Chunk directory not found!"; exit 1; }

for folder in *; do
  # Skip if not a directory or doesn't contain a |
  if [[ ! -d "$folder" || "$folder" != *"|"* ]]; then
    continue
  fi

  # Split folder name into dongle ID and timestamp
  IFS='|' read -r dongle_id timestamp <<< "$folder"

  # Create nested directory structure
  nested_dir="$dongle_id/$timestamp"

  if [[ -e "$dongle_id" && ! -d "$dongle_id" ]]; then
    echo "🚫 A file named '$dongle_id' exists. Renaming it to '${dongle_id}_file_backup'"
    mv "$dongle_id" "${dongle_id}_file_backup"
  fi

  mkdir -p "$nested_dir"

  # Move all contents
  echo "Reorganizing $folder → $nested_dir"
  mv "$folder"/* "$nested_dir/"

  # Remove old flat folder
  rmdir "$folder"
done

echo "✅ Log directory restructuring complete."
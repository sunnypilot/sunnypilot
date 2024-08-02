#!/usr/bin/env bash

# Check if the correct number of arguments are provided
if [ "$#" -lt 2 ]; then
  echo "Error: Missing required arguments."
  echo "Usage: $0 \"ext1,ext2,...\" \"dir1,dir2,...\" [expect_no_match]"
  exit 1
fi

# Convert comma-separated lists of extensions and directory patterns to arrays
IFS=',' read -r -a file_extensions <<< "$1"
IFS=',' read -r -a dir_patterns <<< "$2"

# Boolean argument to determine the script's behavior when matches are found
expect_no_match=${3:-true} # Default to true if not provided

# Validate that file_extensions and dir_patterns are not empty
if [ ${#file_extensions[@]} -eq 0 ]; then
  echo "Error: No file extensions provided."
  exit 1
fi

if [ ${#dir_patterns[@]} -eq 0 ]; then
  echo "Error: No directory patterns provided."
  exit 1
fi

# Define the command and arguments as an array
find_command=(find . \( -false)

for ext in "${file_extensions[@]}"; do
  find_command+=(-o -type f -name "*$ext")
done
for dir in "${dir_patterns[@]}"; do
  find_command+=(-o -type d -path "$dir")
done

find_command+=(\) -print)

# Debug print
echo "Executing find_command ${find_command[@]}"
# Execute the find command
FOUND=$("${find_command[@]}")

# Function to handle found matches
handle_found() {
  local count=$(echo "$FOUND" | grep -c '^')
  if [ "$expect_no_match" = true ]; then
    echo "Failure: Unexpected match$( [ "$count" -gt 1 ] && echo "es" ) found ($count):"
    echo "$FOUND"
    exit 1
  else
    echo "Success: Expected match$( [ "$count" -gt 1 ] && echo "es" ) found ($count):"
    echo "$FOUND"
    exit 0
  fi
}

# Function to handle no matches found
handle_not_found() {
  if [ "$expect_no_match" = false ]; then
    echo "Failure: Expected matches not found."
    exit 1
  else
    echo "Success: No matches found as expected."
    exit 0
  fi
}

# Check if any files or directories are found and handle accordingly
if [ -n "$FOUND" ]; then
  handle_found
else
  handle_not_found
fi

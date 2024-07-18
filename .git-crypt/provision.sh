#!/bin/bash

# Check if gpg is installed
if ! command -v gpg &> /dev/null; then
  echo "gpg could not be found. Please install gpg to continue."
  exit 1
fi

# Check if git-crypt is installed
if ! command -v git-crypt &> /dev/null; then
  # Check if /TICI file exists
  if [ -f "/TICI" ]; then
    echo "/TICI file detected. Attempting to install git-crypt..."
    sudo apt update && sudo apt install git-crypt -y
  else
    echo "git-crypt could not be found. Please install git-crypt to continue."
    exit 1
  fi
fi

# Attempt to unlock with git-crypt
if git-crypt unlock &> /dev/null; then
    echo "git-crypt unlock successful. You already have access."
    exit 0
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
no_prompt=0
# Attempt to retrieve name and email from git config, default to "undefined"
name=$(git config --get user.name)
email=$(git config --get user.email)
name=${name:-"undefined"}
email=${email:-"undefined"}
passphrase=""

# Function to display help message
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --name <name>             Set the user's name. Default is git config user.name or 'undefined'."
    echo "  --email <email>           Set the user's email. Default is git config user.email or 'undefined'."
    echo "  --passphrase <passphrase> Set the passphrase for the GPG key."
    echo "  --no-prompt               Run without interactive prompts, using defaults or provided values."
    echo "  -h, --help                Display this help message and exit."
    echo ""
    exit 0
}

# Check for help flag before parsing other arguments
for arg in "$@"; do
    case $arg in
        -h|--help)
            show_help
            ;;
    esac
done

# Parse named arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --name) name="$2"; shift ;;
        --email) email="$2"; shift ;;
        --passphrase) passphrase="$2"; shift ;;
        --no-prompt) no_prompt=1 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# No need to prompt for missing information if no-prompt is enabled or defaults are used

# Set protection line based on passphrase
if [[ -z "$passphrase" ]]; then
    protection_line="%no-protection"
else
    protection_line="Passphrase: $passphrase"
fi

# Generate and process GPG key
GPG_OUTPUT=$(echo "
%echo Generating a basic OpenPGP key
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: $name
Name-Comment: Generated from git config or default
Name-Email: $email
Expire-Date: 0
$protection_line
%commit
%echo done
" | gpg --batch --generate-key - 2>&1)

# Extract and export the key ID
KEY_ID=$(echo "$GPG_OUTPUT" | grep -o '[0-9A-F]\{40\}' | head -n 1)
if [ -z "$KEY_ID" ]; then
    echo "Failed to generate GPG key or extract key ID."
    exit 1
fi

INSTALL_KEY_PATH=${DIR}/keys/install_new_key_sp
mkdir -p ${INSTALL_KEY_PATH}
gpg --export $KEY_ID > ${INSTALL_KEY_PATH}/$KEY_ID.gpg
git add ${INSTALL_KEY_PATH}/$KEY_ID.gpg
git commit -m "Add new public key to install."
git push

echo "Public key exported to ${INSTALL_KEY_PATH}/${KEY_ID}.gpg"
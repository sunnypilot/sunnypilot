#!/bin/env sh

persist_dir=/persist
target_dir=${persist_dir}/comma
# Change target dir from sunnylink to comma to make this no longer a test


# Function to remount /persist as read-only
cleanup() {
    echo "Remounting ${persist_dir} as read-only..."
    sudo mount -o remount,ro ${persist_dir}
}

# Function to check and backup existing keys
backup_keys() {
    if [ -f "id_rsa" ] || [ -f "id_rsa.pub" ]; then
        timestamp=$(date +%s)
        backup_base="id_rsa_backup_$timestamp"
        backup_private="$backup_base"
        backup_public="${backup_base}.pub"

        # Ensure we're not overwriting an existing backup
        counter=0
        while [ -f "$backup_private" ] || [ -f "$backup_public" ]; do
            counter=$((counter + 1))
            backup_private="${backup_base}_$counter"
            backup_public="${backup_base}_$counter.pub"
        done

        # Backup the keys
        cp id_rsa "$backup_private"
        cp id_rsa.pub "$backup_public"

        # Verify the backup
        original_private_hash=$(sha256sum id_rsa | cut -d ' ' -f 1)
        backup_private_hash=$(sha256sum "$backup_private" | cut -d ' ' -f 1)
        original_public_hash=$(sha256sum id_rsa.pub | cut -d ' ' -f 1)
        backup_public_hash=$(sha256sum "$backup_public" | cut -d ' ' -f 1)

        if [ "$original_private_hash" = "$backup_private_hash" ] && [ "$original_public_hash" = "$backup_public_hash" ]; then
            echo "Backup verified successfully."
            # Safe to delete original keys after successful backup verification
        else
            echo "Backup verification failed. Aborting operation."
            exit 1
        fi

        echo "Existing keys backed up as $backup_private and $backup_public"
    fi
}

# Trap any signal that exits the script to run cleanup function
trap cleanup EXIT

# Remount /persist as read-write
sudo mount -o remount,rw ${persist_dir}

# Ensure the directory exists
mkdir -p ${target_dir}
cd ${target_dir}

# Check for and backup existing keys
#backup_keys

# Generate new keys
if ! ssh-keygen -t rsa -b 4096 -m PEM -f id_rsa -N ''; then
    echo "Failed to generate new RSA keys. Exiting..."
    exit 1
fi

# Convert the generated SSH public key to PEM format and store it temporarily
if ! openssl rsa -pubout -in id_rsa -out id_rsa.pub -outform PEM; then
    echo "Failed to convert the public key to PEM format. Exiting..."
    exit 1
fi

# Display the public key
echo "Displaying the public key:"
cat id_rsa.pub

# Cleanup will be called automatically due to trap on EXIT
#echo "Operation completed successfully. System will reboot now."
#sudo reboot

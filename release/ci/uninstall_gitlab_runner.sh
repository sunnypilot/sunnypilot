#!/bin/bash
# Define directories and user
GITLAB_BASE_DIR="/data/gitlab"
BIN_DIR="$GITLAB_BASE_DIR/bin"
BUILDS_DIR="$GITLAB_BASE_DIR/builds"
OPENPILOT_DIR="$GITLAB_BASE_DIR/openpilot"
LOGS_DIR="$GITLAB_BASE_DIR/logs"
CACHE_DIR="$GITLAB_BASE_DIR/cache"
RUNNER_USERNAME="gitlab-runner"
# Define the systemd service name
SERVICE_NAME="gitlab-runner"
USER_GROUPS="comma,gpu,gpio,sudo"

# Function to stop and disable the systemd service
stop_service() {
    sudo systemctl stop ${SERVICE_NAME}
    sudo systemctl disable ${SERVICE_NAME}
}

# Function to remove the systemd service file
remove_service_file() {
    sudo rm /etc/systemd/system/${SERVICE_NAME}.service
    sudo systemctl daemon-reload
}

# Function to delete the GitLab Runner directories
delete_directories() {
    sudo rm -rf "$BIN_DIR/gitlab-runner"
    sudo rm -rf "$GITLAB_BASE_DIR" "$BIN_DIR" "$BUILDS_DIR" "$LOGS_DIR" "$CACHE_DIR" "$OPENPILOT_DIR"
}

# Function to remove the GitLab Runner user
delete_user() {
    for group in ${USER_GROUPS//,/ }
    do
       sudo gpasswd -d ${RUNNER_USERNAME} ${group}
    done
    sudo userdel -r ${RUNNER_USERNAME}
}

# Function to remove sudoers entry
remove_sudoers_entry() {
    sudo sed -i.bak "/${RUNNER_USERNAME} ALL=(ALL) NOPASSWD: ALL/d" /etc/sudoers
}

# Make filesystem writable
sudo mount -o remount rw /

# Ensure filesystem is remounted as read-only on script exit
trap "sudo mount -o remount ro /" EXIT

# Call functions
stop_service
remove_service_file
delete_directories
delete_user
remove_sudoers_entry
# End of uninstall script

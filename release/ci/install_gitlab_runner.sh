#!/bin/bash
set -e

# Check if script arguments are present, if not exit the script
if [ $# -eq 0 ]; then
    echo "No arguments provided. A GitLab token is required to run this script."
    exit 1
fi

# Constants
GITLAB_RUNNER_DOWNLOAD_URL="https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-arm64"
GITLAB_RUNNER_USER_NAME="gitlab-runner"
USER_GROUPS="comma,gpu,gpio,sudo"
GITLAB_BASE_DIR="/data/gitlab"
GITLAB_BIN_DIR="${GITLAB_BASE_DIR}/bin"
GITLAB_BUILDS_DIR="${GITLAB_BASE_DIR}/builds"
GITLAB_LOGS_DIR="${GITLAB_BASE_DIR}/logs"
GITLAB_CACHE_DIR="${GITLAB_BASE_DIR}/cache"
GITLAB_OPENPILOT_DIR="${GITLAB_BASE_DIR}/openpilot"
SERVICE_NAME="gitlab-runner"

create_gitlab_runner_directories() {
    sudo mkdir -p "$GITLAB_BIN_DIR" "$GITLAB_BUILDS_DIR" "$GITLAB_LOGS_DIR" "$GITLAB_CACHE_DIR" "$GITLAB_OPENPILOT_DIR"
    mkdir -p "/data/openpilot"
    sudo chown -R comma:comma "/data/openpilot"
}

download_and_setup_gitlab_runner() {
    sudo curl -L --output "$GITLAB_BIN_DIR/gitlab-runner" "$GITLAB_RUNNER_DOWNLOAD_URL"
    sudo chmod +x "$GITLAB_BIN_DIR/gitlab-runner"
}

setup_gitlab_runner_user() {
    sudo useradd --comment 'GitLab Runner' --create-home --home-dir ${GITLAB_BASE_DIR} ${GITLAB_RUNNER_USER_NAME} --shell /bin/bash -G ${USER_GROUPS} || sudo usermod -aG ${USER_GROUPS} ${GITLAB_RUNNER_USER_NAME}
    export GITLAB_BASE_DIR # Export it to make it available to sub-processes
    sudo -u ${GITLAB_RUNNER_USER_NAME} bash -c "truncate -s 0 '${GITLAB_BASE_DIR}/.bash_logout'"
}

create_sudoers_entry() {
    sudo grep -qxF "${GITLAB_RUNNER_USER_NAME} ALL=(ALL) NOPASSWD: ALL" /etc/sudoers || echo "${GITLAB_RUNNER_USER_NAME} ALL=(ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers
}

generate_gitlab_config_file() {
    cat <<EOL | sudo tee "$GITLAB_BASE_DIR/config.toml"
[[runners]]
  name = "tici"
  url = "https://gitlab.com/"
  token = "$1"
  executor = "shell"
  builds_dir = "$GITLAB_BUILDS_DIR"
  [runners.custom_build_dir]
  [runners.docker]
    volumes = ["$GITLAB_CACHE_DIR:/cache"]
  [runners.cache]
    MaxUploadedArchiveSize = 0
  [runners.custom]
    config_exec = "$GITLAB_LOGS_DIR"
EOL
}

set_gitlab_directory_permissions() {
    sudo chown -R ${GITLAB_RUNNER_USER_NAME}:comma "$GITLAB_BASE_DIR"
    sudo chmod g+rwx "$GITLAB_BASE_DIR"
    sudo chmod g+s "$GITLAB_BASE_DIR"
}

# Please note that when the gitlab runner is started, linux implicitly executes "source /etc/profile" for every logged shell. This will make scons available
create_gitlab_runner_service() {
    cat <<EOL | sudo tee /etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=GitLab Runner
After=syslog.target network.target
ConditionFileIsExecutable=$GITLAB_BIN_DIR/gitlab-runner
[Service]
StartLimitInterval=5
StartLimitBurst=10
ExecStart=/usr/bin/unshare -m -- sh -c 'mount --bind $GITLAB_OPENPILOT_DIR /data/openpilot && exec $GITLAB_BIN_DIR/gitlab-runner "run" "--working-directory" "$GITLAB_BUILDS_DIR" "--config" "$GITLAB_BASE_DIR/config.toml" "--service" "gitlab-runner" "--syslog" "--user" "${GITLAB_RUNNER_USER_NAME}"'
Restart=always
RestartSec=120
[Install]
WantedBy=multi-user.target
EOL
}

start_gitlab_runner_service() {
    sudo systemctl daemon-reload
    sudo systemctl disable gitlab-runner # Intentionally making sure the service is NOT enabled on boot.
    sudo systemctl start gitlab-runner
}

# Make the filesystem writable
sudo mount -o remount,rw /

# Ensure filesystem is remounted as read-only on script exit
trap "sudo mount -o remount,ro /" EXIT

# Call functions
setup_gitlab_runner_user
create_sudoers_entry
create_gitlab_runner_directories
download_and_setup_gitlab_runner
generate_gitlab_config_file "$1"
set_gitlab_directory_permissions
create_gitlab_runner_service
start_gitlab_runner_service

# End of install script

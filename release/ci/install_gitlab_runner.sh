#!/bin/bash

# We need RW for the install process
sudo mount -o remount rw /

# Ensure filesystem is remounted as read-only on script exit
trap "sudo mount -o remount ro /" EXIT

# Define directories
BASE_DIR="/data/gitlab"
BIN_DIR="$BASE_DIR/bin"
CONFIG_DIR="$BASE_DIR"
BUILDS_DIR="$BASE_DIR/builds"
OPENPILOT_DIR="$BASE_DIR/openpilot"
LOGS_DIR="$BASE_DIR/logs"
CACHE_DIR="$BASE_DIR/cache"
GITLAB_RUNNER_USERNAME="gitlab-runner"
GROUPS_NEEDED="comma,gpu,gpio,sudo"

# Create necessary directories
sudo mkdir -p "$BIN_DIR" "$BUILDS_DIR" "$LOGS_DIR" "$CACHE_DIR" "$OPENPILOT_DIR"

# Download the GitLab Runner binary
sudo curl -L --output "$BIN_DIR/gitlab-runner" "https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-arm64"

# Give it permission to execute
sudo chmod +x "$BIN_DIR/gitlab-runner"

# Create a GitLab Runner user
sudo useradd --comment 'GitLab Runner' --create-home --home-dir ${BASE_DIR} ${GITLAB_RUNNER_USERNAME} --shell /bin/bash -G ${GROUPS_NEEDED} || sudo usermod -aG ${GROUPS_NEEDED} gitlab-runner
grep -qxF 'gitlab-runner ALL=(ALL) NOPASSWD: ALL' /etc/sudoers || echo 'gitlab-runner ALL=(ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers #Giving us SUDO rights

# Clean bash_logout as it break gitlab pipelines
sudo truncate -s 0 ${BASE_DIR}/.bash_logout

# Create a configuration file
cat <<EOL | sudo tee "$CONFIG_DIR/config.toml"
[[runners]]
  name = "tici"
  url = "https://gitlab.com/"
  token = "$1"
  executor = "shell"
  builds_dir = "$BUILDS_DIR"
  [runners.custom_build_dir]
  [runners.docker]
    volumes = ["$CACHE_DIR:/cache"]
  [runners.cache]
    MaxUploadedArchiveSize = 0
  [runners.custom]
    config_exec = "$LOGS_DIR"
EOL

# Set permissions
sudo chown -R ${GITLAB_RUNNER_USERNAME}:comma "$BASE_DIR"
sudo chmod g+rwx "$BASE_DIR"
sudo chmod g+s "$BASE_DIR"


# Create a systemd service file for gitlab-runner
cat <<EOL | sudo tee /etc/systemd/system/gitlab-runner.service
[Unit]
Description=GitLab Runner
After=syslog.target network.target
ConditionFileIsExecutable=$BIN_DIR/gitlab-runner

[Service]
StartLimitInterval=5
StartLimitBurst=10
ExecStart=/usr/bin/unshare -m -- sh -c 'mount --bind $OPENPILOT_DIR /data/openpilot && exec $BIN_DIR/gitlab-runner "run" "--working-directory" "$BUILDS_DIR" "--config" "$CONFIG_DIR/config.toml" "--service" "gitlab-runner" "--syslog" "--user" "${GITLAB_RUNNER_USERNAME}"'

Restart=always
RestartSec=120

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and start gitlab-runner
sudo systemctl daemon-reload
sudo systemctl disable gitlab-runner # Intentionally, making sure the service is NOT enabled on boot.
sudo systemctl start gitlab-runner

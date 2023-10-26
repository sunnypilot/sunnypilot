#!/bin/bash

# Define the service name
SERVICE_NAME="gitlab-runner"

# Function to control the service
control_service() {
    local action=$1  # Store the function argument in a local variable
    sudo systemctl $action ${SERVICE_NAME}
}

service_exists_and_is_loaded() {
    systemctl --quiet is-enabled ${SERVICE_NAME}
}

# Check for required argument
if [[ -z $1 ]] || { [[ $1 != "start" ]] && [[ $1 != "stop" ]]; }; then
    echo "Usage: $0 {start|stop}"
    exit 1
fi

# Check if the service is actually present on the system
if ! service_exists_and_is_loaded; then
    echo "Service ${SERVICE_NAME} does not exist on the system."
    exit 0  # Graceful exit because it's not an error
fi

# Store the script argument in a descriptive variable
ACTION=$1

# Trap EXIT signal (Ctrl+C) and stop the service
trap 'control_service stop' SIGINT SIGKILL EXIT

# Enter the main loop
while true; do
    control_service $ACTION  # Call the function with the specified action
    sleep 1  # Pause before the next iteration
done

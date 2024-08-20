#!/bin/bash

# Define the repository directory and Python script
REPO_DIR="/home/sven/rpi-ws281x-fire/"
PYTHON_SCRIPT="fire.py"
SSH_KEY="/home/sven/.ssh/id_rsa" #/home/sven/.ssh/id_ed25519
SSH_PASSPHRASE="123"

# Function to check internet connection
check_internet() {
    wget -q --spider http://google.com
    return $?
}

# Function to start SSH agent and add the SSH key using expect
start_ssh_agent() {
    eval "$(ssh-agent -s)"
    #/usr/bin/expect <<EOF
    set timeout -1
    spawn ssh-add "$SSH_KEY"
    expect "Enter passphrase"
    send -- "$SSH_PASSPHRASE\r"
    expect eof
}

# Start the SSH agent and add the SSH key
#start_ssh_agent / expect ccurrently not used
eval "$(ssh-agent -s)"
ssh-add "$SSH_KEY"

# Ensure SSH_AGENT_PID and SSH_AUTH_SOCK are set
if [ -z "$SSH_AGENT_PID" ] || [ -z "$SSH_AUTH_SOCK" ]; then
    echo "SSH agent not properly started. Still continue..."
fi

# Navigate to the repository directory
cd "$REPO_DIR" || { echo "Repository directory not found!"; exit 1; }

# Check internet connection
if check_internet; then
    echo "Internet connection available. Pulling latest changes from the repository..."
    sudo -u sven git pull --rebase
else
    echo "No internet connection. Skipping git pull."
fi

# Start the Python script
echo "Starting Python script..."
sudo python3 "$PYTHON_SCRIPT"

# Kill the SSH agent after the script is done
kill $SSH_AGENT_PID

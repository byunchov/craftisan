#!/bin/bash

# Check for the correct number of arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <script_path>"
    exit 1
fi

# Get the script path and name
script_path=$1
script_name=$(basename "$script_path")
file_name="${script_name%.*}"

# Copy the script to /usr/local/bin/
sudo cp "$script_path" /usr/local/bin/"$file_name"

# Make it executable
sudo chmod +x /usr/local/bin/"$file_name"

echo "Script '$script_name' has been installed to /usr/local/bin/"

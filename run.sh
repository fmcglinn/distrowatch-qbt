#!/bin/bash

# Define paths
PROJECT_DIR="/opt/distrowatch-qbt"
PYTHON="$PROJECT_DIR/venv/bin/python"
SCRIPT="$PROJECT_DIR/distrowatch-qbt.py"
LOG_DIR="$PROJECT_DIR/logs/"
LOG_FILE="$LOG_DIR/torrent_fetcher.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Rotate logs, keeping only the last 10 runs
ls -tp "$LOG_DIR" | grep -v '/$' | tail -n +11 | xargs -I {} rm -- "$LOG_DIR/{}"

# Run the script and log output
TIMESTAMP=$(date "+%Y-%m-%d_%H-%M-%S")
$PYTHON $SCRIPT &> "$LOG_DIR/torrent_fetcher_$TIMESTAMP.log"

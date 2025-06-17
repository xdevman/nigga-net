#!/bin/bash
while true; do
    echo "Starting bot..."
    python3.12 bot.py  # scrpit file
    echo "Bot crashed. Restarting in 5 seconds..."
    sleep 5
done
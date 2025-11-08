#!/bin/bash
# PawMatch CLI Launcher
echo "🐾 Launching PawMatch Interactive Chatbot..."
echo ""

cd "$(dirname "$0")"

# Use the virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    python chat_cli.py
else
    python3 chat_cli.py
fi

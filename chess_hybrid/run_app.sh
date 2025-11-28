#!/bin/bash

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$DIR/venv/bin/activate"

# Run the application
# Ensure PYTHONPATH includes the project root so imports work correctly
export PYTHONPATH="$DIR:$PYTHONPATH"

python "$DIR/chess_mind_app.py"

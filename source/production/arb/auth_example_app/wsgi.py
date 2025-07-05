"""
WSGI entry point for the Auth Example App.

This file enables the application to be run via a WSGI server
(e.g., Gunicorn or uWSGI) or directly via `flask run` or `python wsgi.py`.

Usage:
    # Direct Python execution
    python wsgi.py
    
    # Flask CLI
    flask --app wsgi run --debug -p 5000
    
    # WSGI server (production)
    gunicorn wsgi:app
    
    # Environment variables
    export FLASK_APP=wsgi
    export FLASK_ENV=development
    flask run
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from arb.auth_example_app.app import create_app
logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

# Set default environment for development
os.environ.setdefault('FLASK_ENV', 'development')

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    logger.debug("Starting Auth Example App from wsgi.py")
    print("=" * 60)
    print("Auth Example App - Multiple Roles Demonstration")
    print("=" * 60)
    print("Example users created:")
    print("- admin@example.com (admin)")
    print("- editor@example.com (editor)")
    print("- qaqc@example.com (qaqc)")
    print("- editor_qaqc@example.com (editor, qaqc)")
    print("- reviewer@example.com (reviewer)")
    print("- manager@example.com (manager, reviewer)")
    print("- user@example.com (user)")
    print()
    print("Access the app at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
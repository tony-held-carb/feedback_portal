"""
WSGI entry point for the ARB Feedback Portal Flask application.

This module provides the Flask application instance for deployment via WSGI servers
(Gunicorn, uWSGI) or direct execution via Flask CLI.

The application is designed to be run from the production directory ($prod) using:
  cd $prod
  flask --app arb/wsgi run --debug --no-reload -p 2113

Module_Attributes:
  app (Flask): The Flask application instance created by create_app().
  logger (logging.Logger): Logger instance for this module.

Usage Examples:
  * Development (from $prod directory):
      flask --app arb/wsgi run --debug --no-reload -p 2113
  
  * Production with Gunicorn:
      gunicorn arb.wsgi:app --bind 0.0.0.0:2113
  
  * Direct execution (for debugging):
      python arb/wsgi.py

Environment Variables:
  * FLASK_APP: Set to 'arb.wsgi' for Flask CLI
      * Sets the default name for the flask app if not specified.
      * "flask run" is equivalent to "flask --app FLASK_APP run"
      * Likely FLASK_APP=app.py or FLASK_APP=wsgi
  * FLASK_ENV: 'development' or 'production'
      * Can be 'development' or 'production'
      * development enables debug mode, auto-reload, and detailed error pages
        production disables them
      * Likely want FLASK_ENV=development for CARB development
  * FLASK_DEBUG: 1 for debug mode, 0 for production
      * 1 enables the interactive browser debugger (Werkzeug);
      * 0 disables it.
  * PYTHONPATH: Should include $prod for module resolution
      * Adds directories to Python's module resolution path (sometimes needed for imports)

app.run Arguments:
  * host: Controls which network interfaces the Flask server binds to
    * '127.0.0.1' (default): Only accepts connections from the local machine
      * More secure, only local access
    * '0.0.0.0': Accepts connections from any network interface (including external)
      * Less secure, accessible from network/Internet
  * threaded: Enables multi-threading for handling concurrent requests
    * False (default): Single-threaded - handles one request at a time
      * Single-threaded: Simpler, but can't handle concurrent users well
    * True: Multi-threaded - can handle multiple requests simultaneously
      * Multi-threaded: Better for multiple users, but uses more resources

Notes:
  * The application expects to be run from the production directory ($prod)
  * Debug mode is enabled by default for development
  * Auto-reload is disabled for faster startup and stability
  * Port 2113 is the standard development port
  * For PyCharm debugging, set FLASK_ENV=development and FLASK_DEBUG=0.
  * Flask configuration precedence:
      * The effective behavior of your Flask app depends on how it's launched and which
        configuration values are set at various levels. The following precedence applies:
      * Precedence Order (from strongest to weakest):
          1. Arguments passed directly to `app.run(...)`
          2. Flask CLI command-line options
              - e.g., `flask run --port=8000` overrides any FLASK_RUN_PORT setting.
          3. Environment variables
              - e.g., FLASK_ENV, FLASK_DEBUG, FLASK_RUN_PORT
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from arb.logging.arb_logging import setup_app_logging
from arb.portal.app import create_app

# Setup application logging
machine_name = os.environ.get('MACHINE_NAME', None)
app_name = "arb_portal"

# Create timestamp for log filename
timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

# Create a more descriptive log filename with timestamp
if machine_name is None:
  log_filename = f"{app_name}_created_{timestamp}"
else:
  log_filename = f"{app_name}_{machine_name}_created_{timestamp}"

setup_app_logging(log_filename)

# Get logger for this module
logger = logging.getLogger(__name__)

# Log file loading for diagnostics
file_path = Path(__file__)
logger.debug(f'Loading WSGI file: "{file_path.name}" from "{file_path}"')

# Create the Flask application
app = create_app()

# Log effective logging levels for diagnostics
root_level = logging.getLogger().getEffectiveLevel()
logger.info(f"[DIAGNOSTIC] Root logger level: {logging.getLevelName(root_level)}")
logger.info(f"[DIAGNOSTIC] {__name__} logger level: {logging.getLevelName(logger.getEffectiveLevel())}")

# Development server configuration
if __name__ == "__main__":
  logger.info("Starting Flask development server")
  logger.info("For production, use: gunicorn arb.wsgi:app")

  app.run(
    #  host='0.0.0.0',      # Bind to all interfaces
    # port=2113,           # Standard development port
    debug=True,  # Enable debug mode for development <--- (debug=True) is critical for PyCharm-based debug mode
    use_reloader=False,  # Disable auto-reload for stability
    #  threaded=True        # Enable threading for concurrent requests
  )

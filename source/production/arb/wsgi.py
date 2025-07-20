"""
  WSGI entry point for serving the ARB Feedback Portal Flask app.

  This file enables the application to be run via a WSGI server
  (e.g., Gunicorn or uWSGI) or directly via `flask run` or `python wsgi.py`.

  It provides detailed notes for various execution contexts, Flask CLI behavior,
  debugging strategies, and developer workflows including PyCharm integration.

  Args:
    None

  Returns:
    None

  Attributes:
    app (Flask): The Flask application instance created by create_app().
    logger (logging.Logger): Logger instance for this module.

  Examples:
    # Run with Flask CLI:
    #   flask run --app wsgi
    # Run directly:
    #   python wsgi.py
    # Run with Gunicorn:
    #   gunicorn arb.wsgi:app

  Notes:
    - See the detailed notes below for configuration, environment variables, and best practices.
    - Use app.run(debug=True) for development and debugging, but not for production deployment.
    - The project root directory is "feedback_portal".
    - For PyCharm debugging, set FLASK_ENV=development and FLASK_DEBUG=0.

  -----------------------------------------------------------------------------
  Note on running Flask Apps:

  1) You can run a flask app from the CLI in two ways:
    * python <file_name_with_app>
      * run flask app directly from python without the flask CLI
      * Errors shown in terminal; browser only shows generic 500 unless debug=True in source code
    * flask run <optional_file_name_with_app>
      * uses the Flask CLI
      * makes use of Flask related environment variables and command line arguments

  2) Flask configuration precedence:
      The effective behavior of your Flask app depends on how it's launched and which
      configuration values are set at various levels. The following precedence applies:
      Precedence Order (from strongest to weakest):
        1. Arguments passed directly to `app.run(...)`
        2. Flask CLI command-line options
            - e.g., `flask run --port=8000` overrides any FLASK_RUN_PORT setting.
        3. Environment variables
            - e.g., FLASK_ENV, FLASK_DEBUG, FLASK_RUN_PORT

  3) Environmental variables and running from the Flask CLI
      * FLASK_APP:
          sets the default name for the flask app if not specified.
          "flask run" is equivalent to "flask --app FLASK_APP run"
          Likely FLASK_APP=app.py or FLASK_APP=wsgi
      * FLASK_ENV:
          can be 'development' or 'production'
          development enables debug mode, auto-reload, and detailed error pages,
          production disables them.
          Likely want FLASK_ENV=development for CARB development
      * FLASK_DEBUG:
          1 enables the interactive browser debugger (Werkzeug);
          0 disables it.
      * PYTHONPATH:
          Adds directories to Python's module resolution path (sometimes needed for imports)

  4) Flask CLI arguments
      * key options
        * --app <file_name>
        * --debug or --no-debug
          * determines if the Werkzeug browser debugger is on/off
        * --no-reload <-- faster load time and does not restart app on source code changes

  5) Commonly used arguments for `app.run()`:
      * host (str, optional): The IP address to bind to.
          Defaults to `'127.0.0.1'`. Use `'0.0.0.0'` to make the app
          publicly accessible (e.g., on a local network).
      * port (int, optional): The port number to listen to.
          Defaults to `5000`.
      * debug (bool, optional): Enables debug mode, which activates
          auto-reload and the interactive browser debugger. Defaults to `None`.
      * use_reloader (bool, optional): Enables the auto-reloader to restart
          the server on code changes. Defaults to `True` if debug is enabled.
      * use_debugger (bool, optional): Enables the interactive debugger
          in the browser when errors occur. Defaults to `True` if debug is enabled.
      * threaded (bool, optional): Run the server in multithreaded mode.
          Useful for handling multiple concurrent requests. Defaults to `False`.
      * processes (int, optional): Number of worker processes for handling requests.
          Mutually exclusive with `threaded=True`. Defaults to `1`.
      * load_dotenv (bool, optional): Whether to load environment variables from
          a `.env` file. Defaults to `True`.

  6) Best practices:
     * Use app.run(debug=True) in wsgi.py for development (not for production)
     * Use 'development' over 'production' until product is final
     * For browser-based testing: flask run --app wsgi
     * For PyCharm debugging: Run wsgi.py with debug=True, FLASK_ENV=development, FLASK_DEBUG=0
     * Combined workflow: PyCharm + browser, debug=True, FLASK_ENV=development, FLASK_DEBUG=1

  7) Root directory notes:
     - The project root directory is "feedback_portal"
     - If the app is run from wsgi.py at feedback_portal/source/production/arb/wsgi.py
       Path(__file__).resolve().parents[3] → .../feedback_portal
  -----------------------------------------------------------------------------
"""

import logging
from pathlib import Path

from arb.portal.app import create_app
from arb.logging.arb_logging import setup_app_logging

setup_app_logging("arb_portal")

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

app = create_app()

# Log the effective log level for diagnostics
root_level = logging.getLogger().getEffectiveLevel()
logger.info(f"[DIAGNOSTIC] Root logger effective level: {logging.getLevelName(root_level)}")
logger.info(f"[DIAGNOSTIC] {__name__} logger effective level: {logging.getLevelName(logger.getEffectiveLevel())}")

if __name__ == "__main__":
  logger.debug(f"in wsgi.py main")
  app.run(debug=True)  # <--- (debug=True) is critical for PyCharm-based debug mode

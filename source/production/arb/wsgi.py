"""
WSGI entry point for serving the Flask app.

This file enables the application to be run via a WSGI server
(e.g., Gunicorn or uWSGI) or directly via `flask run` or `python wsgi.py`.

It provides detailed notes for various execution contexts, Flask CLI behavior,
debugging strategies, and developer workflows including PyCharm integration.

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
         - These override everything else, including CLI flags and environment variables.

      2. Flask CLI command-line options
         - e.g., `flask run --port=8000` overrides any FLASK_RUN_PORT setting.

      3. Environment variables
         - e.g., FLASK_ENV, FLASK_DEBUG, FLASK_RUN_PORT

2) Environmental variables and running from the Flask CLI

   * FLASK_APP:
      sets the default name for the flask app if not specified.
      "flask run" is equivalent to "flask --app FLASK_APP run"
      Likely FLASK_APP=app.py or FLASK_APP=wsgi
  * FLASK_ENV:
      can be 'development' or 'production'
      development enables debug mode, auto-reload, and detailed error pages,
      production disables them.
      Likely will allways want FLASK_ENV=development for CARB development
  * FLASK_DEBUG:
      1 enables the interactive browser debugger (Werkzeug);
      0 disables it.
  * PYTHONPATH:
      Adds directories to Python's module resolution path (sometimes needed for imports)

3) Flask CLI arguments
    * key options
      * --app <file_name>
      * --debug or --no-debug
        * determines if the Werkzeug browser debugger is on/off
      * --no-reload  <-- faster load time and does not restart app on source code changes

4) Source code app arguments:

    Commonly used arguments for `app.run()`:

    Args:
      * host (str, optional): The IP address to bind to.
          Defaults to `'127.0.0.1'`. Use `'0.0.0.0'` to make the app
          publicly accessible (e.g., on a local network).
      * port (int, optional): The port number to listen on.
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

5) Best practices:
  1. use app.run(debug=True) in the wsgi file except for official release to 3rd parties
    * will give you access to Browser-based call trace or python debugger depending on other factors
  2. Use 'development' over 'production' until product is final.
  3. testing web interactions in browser without python debugger
    * flask run --app wsgi
  4. Debugging with PyCharm (breakpoints + console)
    * Use a Run Configuration:
        * Script: wsgi.py
        * Working Dir: production/arb
        * Env vars: FLASK_ENV=development, FLASK_DEBUG=0
        * app.run(debug=True) in wsgi.py
  5. Combined Workflow (PyCharm + Browser)
    * Run wsgi.py in PyCharm with debug=True
    * Set FLASK_ENV=development, FLASK_DEBUG=1
      * This allows:
        * PyCharm to log & capture
        * Browser to display detailed error trace
        * Breakpoints still work (though sometimes suppressed by Werkzeug internals)

6) Root directory notes:
  - The project root directory is "feedback_portal"
  - if the app is run from wsgi.py file with path: feedback_portal/source/production/arb/wsgi.py
    - Path(__file__).resolve().parents[3] → .../feedback_portal

# todo - work this in, run with: flask --app wsgi run --no-reload

"""

from arb.__get_logger import get_logger
from arb.portal.app import create_app

logger, pp_log = get_logger()
logger.debug("in wsgi.py module")

app = create_app()

if __name__ == "__main__":
  logger.debug("in wsgi.py main")
  app.run(debug=True)  # <--- (debug=True) is critical for PyCharm-based debug mode

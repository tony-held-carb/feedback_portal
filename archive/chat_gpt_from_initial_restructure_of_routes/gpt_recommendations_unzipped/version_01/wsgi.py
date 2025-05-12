"""
WSGI entry point for the Flask application.

This file is used to run the app from a WSGI server (e.g., Gunicorn or uWSGI),
or directly via `python wsgi.py` for development.

Example:
    $ flask run --app wsgi --debug
"""

from arb.portal.app import create_app

app = create_app()

if __name__ == "__main__":
  # Only for development/testing. Use a proper WSGI server in production.
  app.run(host="0.0.0.0", port=5150, debug=True)

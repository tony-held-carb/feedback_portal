"""
WSGI entry point for serving the Flask app.

This file allows the application to be run using a WSGI server like Gunicorn or uWSGI.

Usage:
  gunicorn wsgi:app
  or
  flask run --app wsgi

Make sure the environment variable FLASK_ENV is set to "development" or "production" appropriately.

"""

import arb.__get_logger as get_logger
from arb.portal.app import create_app

logger, pp_log = get_logger.get_logger(__name__, __file__)
logger.debug("in wsgi.py module")

app = create_app()

if __name__ == "__main__":
  logger.debug("in wsgi.py main")
  app.run(debug=True)

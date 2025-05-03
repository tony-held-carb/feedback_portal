"""
WSGI entry point for serving the Flask app.

This file allows the application to be run using a WSGI server like Gunicorn or uWSGI.

Usage:
  gunicorn wsgi:app
  or
  flask run --app wsgi

Make sure the environment variable FLASK_ENV is set to "development" or "production" appropriately.

"""
import logging

from arb.portal.app import create_app

# todo - make this my standard get logger?
# Optional: direct logs to a file
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("source/production/arb/portal/logs/wsgi.log", mode="a"),
        logging.StreamHandler()
    ]
)

app = create_app()

if __name__ == "__main__":
  app.run(debug=True)

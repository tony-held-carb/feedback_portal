# All meaningful logic in accessors.py is covered by these tests. No further tests are needed unless new accessors are added.
import pytest
from unittest.mock import patch
from flask import Flask
import arb.portal.config.accessors as accessors
import os

def test_get_processed_versions_dir():
    app = Flask(__name__)
    with app.app_context():
        app.config["PROCESSED_VERSIONS_DIR"] = "/tmp/processed"
        assert os.path.normpath(str(accessors.get_processed_versions_dir())) == os.path.normpath("/tmp/processed")

def test_get_upload_folder():
    app = Flask(__name__)
    with app.app_context():
        app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
        assert os.path.normpath(str(accessors.get_upload_folder())) == os.path.normpath("/tmp/uploads")

def test_get_payload_save_dir():
    app = Flask(__name__)
    with app.app_context():
        app.config["PAYLOAD_SAVE_DIR"] = "/tmp/payloads"
        assert os.path.normpath(str(accessors.get_payload_save_dir())) == os.path.normpath("/tmp/payloads")

def test_get_app_mode_default():
    app = Flask(__name__)
    with app.app_context():
        assert accessors.get_app_mode() == "dev"

def test_get_app_mode_custom():
    app = Flask(__name__)
    with app.app_context():
        app.config["APP_MODE"] = "prod"
        assert accessors.get_app_mode() == "prod"

def test_get_database_uri():
    app = Flask(__name__)
    with app.app_context():
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://test/test"
        assert accessors.get_database_uri() == "postgresql://test/test"

def test_missing_config_keys():
    app = Flask(__name__)
    with app.app_context():
        with pytest.raises(KeyError):
            accessors.get_processed_versions_dir()
        with pytest.raises(KeyError):
            accessors.get_upload_folder()
        with pytest.raises(KeyError):
            accessors.get_payload_save_dir()
        with pytest.raises(KeyError):
            accessors.get_database_uri() 
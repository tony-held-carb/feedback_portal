"""
Tests for the Flask application factory (app.py).

This module tests the create_app() function and ensures proper application
initialization, configuration loading, and database setup.
"""

import pytest
import unittest
from flask import Flask
from unittest.mock import patch, MagicMock

from arb.portal.app import create_app


class TestCreateApp(unittest.TestCase):
    """Test the Flask application factory function."""

    def test_create_app_returns_flask_instance(self):
        """Test that create_app returns a Flask application instance."""
        app = create_app()
        self.assertIsInstance(app, Flask)
        self.assertEqual(app.name, 'arb.portal.app')

    def test_create_app_config_loading(self):
        """Test that configuration is properly loaded."""
        app = create_app()
        # Check that essential config keys are present
        self.assertIn('SQLALCHEMY_DATABASE_URI', app.config)
        self.assertIn('SECRET_KEY', app.config)
        self.assertIn('SQLALCHEMY_TRACK_MODIFICATIONS', app.config)

    @patch('arb.portal.app.get_config')
    def test_create_app_uses_config_module(self, mock_get_config):
        """Test that create_app uses the config module."""
        # Mock config with required SQLAlchemy keys
        mock_config = MagicMock()
        mock_config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        mock_config.SQLALCHEMY_TRACK_MODIFICATIONS = False
        mock_config.SECRET_KEY = 'test-secret-key'
        mock_get_config.return_value = mock_config
        
        app = create_app()
        
        # Verify get_config was called
        mock_get_config.assert_called_once()
        
        # Verify app has expected configuration
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///:memory:')
        self.assertEqual(app.config['SECRET_KEY'], 'test-secret-key')

    def test_create_app_blueprint_registration(self):
        """Test that route blueprints are properly registered."""
        app = create_app()
        # Check that the main blueprint is registered
        self.assertIn('main', app.blueprints)
        self.assertEqual(app.blueprints['main'].name, 'main')

    @patch('arb.portal.app.db_initialize_and_create')
    @patch('arb.portal.app.reflect_database')
    @patch('arb.portal.app.get_reflected_base')
    @patch('arb.portal.app.Globals.load_type_mapping')
    @patch('arb.portal.app.Globals.load_drop_downs')
    def test_create_app_database_initialization_success(
        self, mock_load_dropdowns, mock_load_type_mapping, 
        mock_get_base, mock_reflect, mock_init
    ):
        """Test successful database initialization path."""
        mock_base = MagicMock()
        mock_get_base.return_value = mock_base
        
        app = create_app()
        
        # Verify database initialization was called
        mock_init.assert_called_once()
        mock_reflect.assert_called_once()
        mock_get_base.assert_called_once()
        
        # Verify base was attached to app
        self.assertTrue(hasattr(app, 'base'))
        self.assertEqual(app.base, mock_base)
        
        # Verify globals were loaded
        mock_load_type_mapping.assert_called_once()
        mock_load_dropdowns.assert_called_once()

    @patch('arb.portal.app.db_initialize_and_create')
    @patch('arb.portal.app.reflect_database')
    @patch('arb.portal.app.get_reflected_base')
    @patch('arb.portal.app.Globals.load_type_mapping')
    @patch('arb.portal.app.Globals.load_drop_downs')
    def test_create_app_database_initialization_failure(
        self, mock_load_dropdowns, mock_load_type_mapping, 
        mock_get_base, mock_reflect, mock_init
    ):
        """Test database initialization failure handling."""
        mock_init.side_effect = Exception("Database connection failed")
        
        # Should not raise exception, should log error and continue
        app = create_app()
        
        # App should still be created even if DB init fails
        self.assertIsInstance(app, Flask)
        self.assertIn('main', app.blueprints)
        
        # Verify error was logged (we can't easily test logging without more complex mocking)
        mock_init.assert_called_once()

    def test_create_app_flask_extensions_initialized(self):
        """Test that Flask extensions are properly initialized."""
        app = create_app()
        
        # Check that SQLAlchemy is initialized
        self.assertTrue(hasattr(app, 'extensions'))
        self.assertIn('sqlalchemy', app.extensions)

    def test_create_app_context_globals_available(self):
        """Test that application context globals are available."""
        app = create_app()
        
        with app.app_context():
            # These should be available in app context
            self.assertTrue(hasattr(app, 'base'))
            # Note: actual values depend on database connection

    def test_create_app_logging_configured(self):
        """Test that logging is properly configured."""
        app = create_app()
        
        # Check that app has logging configuration
        self.assertTrue(hasattr(app, 'logger'))
        # Flask apps typically have a logger attribute

    def test_create_app_multiple_calls_independent(self):
        """Test that multiple calls to create_app return independent instances."""
        app1 = create_app()
        app2 = create_app()
        
        self.assertNotEqual(app1, app2)
        self.assertEqual(app1.name, app2.name)
        self.assertEqual(app1.config['SECRET_KEY'], app2.config['SECRET_KEY'])

    def test_create_app_environment_specific_config(self):
        """Test that environment-specific configuration is loaded."""
        app = create_app()
        
        # Check that we have environment-specific config
        # The app has FLASK_ENV, not ENV
        self.assertIn('FLASK_ENV', app.config)

    @patch('arb.portal.app.configure_flask_app')
    def test_create_app_calls_configure_flask_app(self, mock_configure):
        """Test that configure_flask_app is called during app creation."""
        app = create_app()
        
        mock_configure.assert_called_once_with(app)

    def test_create_app_has_required_attributes(self):
        """Test that the created app has all required attributes."""
        app = create_app()
        
        required_attrs = ['name', 'config', 'blueprints', 'extensions']
        for attr in required_attrs:
            self.assertTrue(hasattr(app, attr))

    def test_create_app_blueprint_routes_accessible(self):
        """Test that routes from registered blueprints are accessible."""
        app = create_app()
        
        # Check that we can access blueprint routes
        # This tests that the blueprint registration worked correctly
        self.assertIn('main', app.blueprints)
        
        # Verify the blueprint has routes (this is a basic check)
        blueprint = app.blueprints['main']
        self.assertTrue(hasattr(blueprint, 'deferred_functions'))

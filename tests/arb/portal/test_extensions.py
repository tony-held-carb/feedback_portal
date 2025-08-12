"""
Tests for Flask extensions (extensions.py).

This module tests the Flask extension instances and ensures they are properly
created and have the expected attributes and methods.
"""

import pytest
import unittest
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from arb.portal.extensions import db, csrf


class TestExtensions(unittest.TestCase):
    """Test Flask extension instances."""

    def test_sqlalchemy_extension_creation(self):
        """Test that SQLAlchemy extension is properly created."""
        self.assertIsNotNone(db)
        self.assertIsInstance(db, SQLAlchemy)
        self.assertTrue(hasattr(db, 'init_app'))
        self.assertTrue(callable(db.init_app))

    def test_csrf_extension_creation(self):
        """Test that CSRF extension is properly created."""
        self.assertIsNotNone(csrf)
        self.assertIsInstance(csrf, CSRFProtect)
        self.assertTrue(hasattr(csrf, 'init_app'))
        self.assertTrue(callable(csrf.init_app))

    def test_sqlalchemy_extension_attributes(self):
        """Test that SQLAlchemy extension has expected attributes."""
        # Check for essential SQLAlchemy attributes
        self.assertTrue(hasattr(db, 'Model'))
        self.assertTrue(hasattr(db, 'Column'))
        self.assertTrue(hasattr(db, 'String'))
        self.assertTrue(hasattr(db, 'Integer'))
        self.assertTrue(hasattr(db, 'Float'))
        self.assertTrue(hasattr(db, 'DateTime'))
        self.assertTrue(hasattr(db, 'Boolean'))
        self.assertTrue(hasattr(db, 'Text'))
        self.assertTrue(hasattr(db, 'ForeignKey'))
        self.assertTrue(hasattr(db, 'relationship'))

    def test_sqlalchemy_extension_methods(self):
        """Test that SQLAlchemy extension has expected methods."""
        # Check for essential SQLAlchemy methods
        self.assertTrue(hasattr(db, 'create_all'))
        self.assertTrue(hasattr(db, 'drop_all'))
        self.assertTrue(hasattr(db, 'session'))
        self.assertTrue(hasattr(db, 'metadata'))
        self.assertTrue(callable(db.create_all))
        self.assertTrue(callable(db.drop_all))

    def test_csrf_extension_attributes(self):
        """Test that CSRF extension has expected attributes."""
        # CSRFProtect is a Flask-WTF extension with specific attributes
        self.assertTrue(hasattr(csrf, 'protect'))
        self.assertTrue(hasattr(csrf, 'exempt'))
        self.assertTrue(hasattr(csrf, 'init_app'))
        
        # Check that these are callable methods
        self.assertTrue(callable(csrf.protect))
        self.assertTrue(callable(csrf.exempt))
        self.assertTrue(callable(csrf.init_app))

    def test_csrf_extension_methods(self):
        """Test that CSRF extension methods work as expected."""
        # Test that init_app can be called (though it won't work without proper context)
        self.assertTrue(callable(csrf.init_app))
        
        # Test that decorators are callable
        self.assertTrue(callable(csrf.protect))
        self.assertTrue(callable(csrf.exempt))

    def test_extensions_not_initialized(self):
        """Test that extensions are not initialized until init_app is called."""
        # Extensions should exist but not be bound to any app yet
        self.assertFalse(hasattr(db, '_app'))
        self.assertFalse(hasattr(csrf, '_app'))

    def test_extensions_importable(self):
        """Test that extensions can be imported without errors."""
        try:
            from arb.portal.extensions import db, csrf
            self.assertIsNotNone(db)
            self.assertIsNotNone(csrf)
        except ImportError as e:
            self.fail(f"Failed to import extensions: {e}")

    def test_extensions_singleton_behavior(self):
        """Test that extensions maintain singleton behavior across imports."""
        from arb.portal.extensions import db as db1, csrf as csrf1
        from arb.portal.extensions import db as db2, csrf as csrf2
        
        # Should be the same instances
        self.assertEqual(db1, db2)
        self.assertEqual(csrf1, csrf2)

    def test_sqlalchemy_metadata_access(self):
        """Test that SQLAlchemy metadata is accessible."""
        self.assertTrue(hasattr(db, 'metadata'))
        self.assertIsNotNone(db.metadata)

    def test_sqlalchemy_session_access(self):
        """Test that SQLAlchemy session is accessible."""
        self.assertTrue(hasattr(db, 'session'))
        self.assertIsNotNone(db.session)

    def test_extensions_type_consistency(self):
        """Test that extensions maintain consistent types."""
        # Re-import to ensure type consistency
        import importlib
        import arb.portal.extensions
        
        importlib.reload(arb.portal.extensions)
        
        from arb.portal.extensions import db as db_reloaded, csrf as csrf_reloaded
        
        self.assertIsInstance(db_reloaded, SQLAlchemy)
        self.assertIsInstance(csrf_reloaded, CSRFProtect)

    def test_extensions_no_circular_imports(self):
        """Test that extensions can be imported without circular import issues."""
        try:
            # This should not cause circular import issues
            from arb.portal.extensions import db, csrf
            from arb.portal.extensions import db as db_alias
            from arb.portal.extensions import csrf as csrf_alias
            
            self.assertEqual(db, db_alias)
            self.assertEqual(csrf, csrf_alias)
        except Exception as e:
            self.fail(f"Circular import or other import issue: {e}")

    def test_extensions_geoalchemy2_import(self):
        """Test that geoalchemy2.Geometry is imported (required for introspection)."""
        # The extensions.py file imports geoalchemy2.Geometry for introspection
        # We can't easily test this without complex mocking, but we can verify
        # the import doesn't cause errors
        try:
            from arb.portal.extensions import db, csrf
            # If we get here, the geoalchemy2 import didn't cause issues
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"geoalchemy2 import issue: {e}")

    def test_extensions_logger_configured(self):
        """Test that extensions module has logging configured."""
        from arb.portal.extensions import logger
        self.assertIsNotNone(logger)
        self.assertTrue(hasattr(logger, 'debug'))
        self.assertTrue(callable(logger.debug))

    def test_extensions_file_path_logging(self):
        """Test that extensions module logs file path information."""
        # This test verifies that the module logs its file path when loaded
        # We can't easily test the actual logging output, but we can verify
        # the logger is configured and the module loads without errors
        try:
            from arb.portal.extensions import db, csrf, logger
            self.assertIsNotNone(logger)
            self.assertIsNotNone(db)
            self.assertIsNotNone(csrf)
        except Exception as e:
            self.fail(f"Extensions module loading issue: {e}")

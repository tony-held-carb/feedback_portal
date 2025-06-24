"""
Test script for authentication system.

This script tests the basic functionality of the authentication system
including user creation, password hashing, and login verification.

Usage:
    python test_auth.py

Notes:
    - This script should be run within the Flask app context.
    - It performs database operations, so use with caution in production.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from arb.portal.app import create_app
from arb.portal.extensions import db
from arb.portal.sqla_models import User

def test_authentication():
    """Test the authentication system functionality."""
    
    app = create_app()
    
    with app.app_context():
        print("Testing Authentication System")
        print("=" * 40)
        
        # Test 1: Create a test user
        print("\n1. Creating test user...")
        try:
            # Check if test user already exists
            existing_user = User.query.filter_by(email='test@example.com').first()
            if existing_user:
                print(f"   Test user already exists: {existing_user}")
                user = existing_user
            else:
                # Create new test user
                user = User()
                user.email = 'test@example.com'
                user.set_password('test@example.com')  # Email as password
                user.is_active = True
                user.is_confirmed = True
                
                db.session.add(user)
                db.session.commit()
                print(f"   Created test user: {user}")
        except Exception as e:
            print(f"   Error creating user: {e}")
            return
        
        # Test 2: Verify password
        print("\n2. Testing password verification...")
        try:
            if user.check_password('test@example.com'):
                print("   ✓ Password verification successful")
            else:
                print("   ✗ Password verification failed")
        except Exception as e:
            print(f"   Error verifying password: {e}")
        
        # Test 3: Test wrong password
        print("\n3. Testing wrong password...")
        try:
            if not user.check_password('wrongpassword'):
                print("   ✓ Wrong password correctly rejected")
            else:
                print("   ✗ Wrong password incorrectly accepted")
        except Exception as e:
            print(f"   Error testing wrong password: {e}")
        
        # Test 4: User statistics
        print("\n4. User statistics...")
        try:
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            confirmed_users = User.query.filter_by(is_confirmed=True).count()
            
            print(f"   Total users: {total_users}")
            print(f"   Active users: {active_users}")
            print(f"   Confirmed users: {confirmed_users}")
        except Exception as e:
            print(f"   Error getting user statistics: {e}")
        
        # Test 5: Flask-Login integration
        print("\n5. Testing Flask-Login integration...")
        try:
            from flask_login import login_user, logout_user, current_user
            
            # Test login
            login_user(user)
            print(f"   ✓ User logged in: {current_user.email}")
            
            # Test logout
            logout_user()
            print(f"   ✓ User logged out")
            
        except Exception as e:
            print(f"   Error testing Flask-Login: {e}")
        
        print("\n" + "=" * 40)
        print("Authentication system test completed!")
        print("\nTest credentials:")
        print("   Email: test@example.com")
        print("   Password: test@example.com")
        print("\nYou can now test the web interface at:")
        print("   http://localhost:5000/auth/login")

if __name__ == '__main__':
    test_authentication() 
"""
Main Flask application factory for the Auth Example App.

This demonstrates how to properly integrate the arb.auth package
into a Flask application with multiple roles support.
"""

from flask import Flask

# Import the auth package
from arb.auth import get_db, init_auth, register_auth_blueprint
# Import extensions from centralized extensions module
from arb.auth_example_app.extensions import db, login_manager, mail
# Import routes
from arb.auth_example_app.routes import admin, main, user_management


def create_app(config_name: str = 'default') -> Flask:
  """
  Application factory for the Auth Example App.

  Args:
      config_name: Configuration to use ('development', 'testing', 'production', 'default')

  Returns:
      Flask: Configured Flask application
  """
  app = Flask(__name__)

  # Load configuration
  from arb.auth_example_app.config import config
  app.config.from_object(config[config_name])

  # Initialize Flask extensions
  db.init_app(app)
  mail.init_app(app)
  login_manager.init_app(app)

  # Initialize the auth package
  init_auth(
    app=app,
    db=db,
    mail=mail,
    login_manager=login_manager
  )

  # Register blueprints
  app.register_blueprint(main.bp)
  app.register_blueprint(admin.bp)
  app.register_blueprint(user_management.bp)

  # Register auth blueprint (from arb.auth)
  register_auth_blueprint(app)

  # Register the User model with SQLAlchemy before creating tables
  from arb.auth.models import get_user_model
  get_user_model()

  # Create database tables
  with app.app_context():
    db.create_all()

    # Create some example users if they don't exist
    create_example_users()

  return app


def create_example_users() -> None:
  """
  Create example users with different role combinations.
  
  This function creates a set of example users with various role
  combinations for testing the authentication system.
  
  Returns:
      None: This function creates users but doesn't return anything.
      
  Examples:
      create_example_users()
  """
  from arb.auth.models import get_user_model
  User = get_user_model()

  # Check if users already exist
  if User.query.count() > 0:
    return

  # Create example users with different role combinations
  users_data = [
    {
      'email': 'admin@example.com',
      'password': 'admin123',
      'roles': ['admin']
    },
    {
      'email': 'editor@example.com',
      'password': 'editor123',
      'roles': ['editor']
    },
    {
      'email': 'qaqc@example.com',
      'password': 'qaqc123',
      'roles': ['qaqc']
    },
    {
      'email': 'editor_qaqc@example.com',
      'password': 'editor_qaqc123',
      'roles': ['editor', 'qaqc']
    },
    {
      'email': 'reviewer@example.com',
      'password': 'reviewer123',
      'roles': ['reviewer']
    },
    {
      'email': 'manager@example.com',
      'password': 'manager123',
      'roles': ['manager', 'reviewer']
    },
    {
      'email': 'user@example.com',
      'password': 'user123',
      'roles': ['user']
    }
  ]

  for user_data in users_data:
    user = User()
    user.email = user_data['email']
    user.set_password(user_data['password'])
    user.set_roles(user_data['roles'])
    user.is_confirmed_col = True  # Skip email confirmation for demo
    get_db().session.add(user)

  get_db().session.commit()
  print("Created example users:")
  for user_data in users_data:
    print(f"  - {user_data['email']} (roles: {', '.join(user_data['roles'])})")


if __name__ == '__main__':
  app = create_app('development')
  app.run(debug=True, host='0.0.0.0', port=5000)

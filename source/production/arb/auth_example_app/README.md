# Auth Example App

A demonstration Flask application showing how to integrate the `arb.auth` package with multiple roles support.

## Features

- **Multiple Roles Support**: Users can have multiple roles (comma-separated)
- **Role-Based Access Control**: Flexible decorators for route protection
- **User Management**: Admin interface for managing users and roles
- **Email Confirmation**: Built-in email confirmation system
- **Password Reset**: Secure password reset functionality
- **Account Lockout**: Protection against brute force attacks

## Project Structure

```
auth_example_app/
├── __init__.py
├── app.py                 # Application factory
├── config.py             # Configuration settings
├── extensions.py         # Flask extension instances
├── routes/
│   ├── __init__.py
│   ├── main.py          # Public routes
│   ├── admin.py         # Admin-only routes
│   └── user_management.py # User management routes
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   └── users.html
│   └── user_management/
│       └── users.html
├── wsgi.py              # WSGI entry point
└── README.md
```

## Key Components

### Extensions (`extensions.py`)

Centralized Flask extension instances to avoid circular imports:

- `db`: SQLAlchemy database instance
- `mail`: Flask-Mail for email functionality
- `login_manager`: Flask-Login for session management

### Application Factory (`app.py`)

Creates and configures the Flask application:

- Loads configuration
- Initializes extensions
- Sets up authentication
- Registers blueprints
- Creates example users

### Configuration (`config.py`)

Environment-specific settings:

- Database URI
- Email settings
- Security settings
- Development/Production configurations

### Routes

- **Main Routes**: Public pages and basic functionality
- **Admin Routes**: Administrative functions (admin role required)
- **User Management**: User CRUD operations (admin role required)

## Installation

1. **Install Dependencies**:
   ```bash
   pip install flask flask-sqlalchemy flask-mail flask-login
   ```

2. **Set Environment Variables** (optional):
   ```bash
   export FLASK_APP=arb.auth_example_app.wsgi
   export FLASK_ENV=development
   ```

3. **Run the Application**:
   ```bash
   # Using WSGI entry point (recommended)
   python -m arb.auth_example_app.wsgi
   
   # Or directly
   python -m arb.auth_example_app.app
   ```

## Example Users

The app creates these example users automatically:

| Email                   | Password       | Roles             |
|-------------------------|----------------|-------------------|
| admin@example.com       | admin123       | admin             |
| editor@example.com      | editor123      | editor            |
| qaqc@example.com        | qaqc123        | qaqc              |
| editor_qaqc@example.com | editor_qaqc123 | editor, qaqc      |
| reviewer@example.com    | reviewer123    | reviewer          |
| manager@example.com     | manager123     | manager, reviewer |
| user@example.com        | user123        | user              |

## Usage Examples

### Route Protection

```python
from arb.auth.decorators import admin_required, has_role, has_any_role

@app.route('/admin-only')
@admin_required
def admin_only():
    return "Admin only content"

@app.route('/editor-only')
@has_role('editor')
def editor_only():
    return "Editor only content"

@app.route('/editor-or-qaqc')
@has_any_role('editor', 'qaqc')
def editor_or_qaqc():
    return "Editor or QAQC content"
```

### Template Usage

```html
{% if current_user.has_role('admin') %}
    <a href="{{ url_for('admin.dashboard') }}">Admin Dashboard</a>
{% endif %}

{% if current_user.has_any_role('editor', 'qaqc') %}
    <a href="{{ url_for('main.editor_tools') }}">Editor Tools</a>
{% endif %}
```

## Integration with arb.auth

This example demonstrates:

1. **Extension Management**: Using `extensions.py` for clean separation
2. **App Factory Pattern**: Proper Flask application factory setup
3. **Blueprint Registration**: Organizing routes into logical groups
4. **Database Integration**: SQLAlchemy setup with the auth package
5. **Role Management**: Multiple roles per user with flexible checking

## Development

- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Local database with email confirmation
- **Session Management**: Flask-Login
- **Email**: Flask-Mail (configured for development)

## Security Features

- Password hashing with Werkzeug
- CSRF protection
- Account lockout after failed attempts
- Email confirmation for new accounts
- Secure password reset tokens
- Role-based access control

## Future Enhancements

- Okta SSO integration
- Fine-grained permissions with Flask-Principal
- API authentication
- Audit logging
- Two-factor authentication 
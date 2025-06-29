# Multiple Roles Support for ARB Feedback Portal

This document describes the enhanced role-based access control system that supports multiple roles per user.

## Overview

The auth package has been updated to support multiple roles per user using a comma-separated approach. This allows users to have combinations of roles like `'editor,qaqc'` or `'reviewer,admin'`.

## Key Changes

### 1. Database Schema
- **Role column size**: Increased from `VARCHAR(32)` to `VARCHAR(255)` to support multiple roles
- **Storage format**: Roles are stored as comma-separated values (e.g., `'editor,qaqc,reviewer'`)

### 2. User Model Enhancements
The `User` model now includes these new methods:

```python
# Get all roles as a list
user.get_roles()  # Returns: ['editor', 'qaqc', 'reviewer']

# Check for specific roles
user.has_role('editor')                    # True if user has 'editor' role
user.has_any_role('editor', 'reviewer')    # True if user has ANY of the roles
user.has_all_roles('editor', 'qaqc')       # True if user has ALL of the roles

# Manage roles
user.add_role('new_role')                  # Add a role
user.remove_role('old_role')               # Remove a role
user.set_roles(['role1', 'role2'])         # Set roles to specific list
```

### 3. New Decorators
Enhanced decorators for flexible access control:

```python
from arb.auth.role_decorators import *

# Single role required
@role_required('editor')
def editor_page():
    pass

# Any of multiple roles
@roles_required('editor', 'reviewer', 'qaqc')
def review_page():
    pass

# All roles required
@all_roles_required('editor', 'qaqc')
def advanced_edit():
    pass

# Admin only (existing functionality)
@admin_required
def admin_panel():
    pass
```

## Migration Process

### Step 1: Update Database Schema
Run this SQL command in your database:

```sql
ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(255);
```

### Step 2: Run Migration Script
Execute the migration script to convert existing single roles to the new format:

```bash
cd source/production/arb/auth
python migrate_roles.py
```

### Step 3: Deploy Updated Code
Deploy the updated User model and new decorators.

## Usage Examples

### In Routes
```python
from arb.auth.role_decorators import roles_required, all_roles_required

@app.route('/edit')
@roles_required('editor', 'reviewer')
def edit_page():
    """Users with 'editor' OR 'reviewer' role can access"""
    return render_template('edit.html')

@app.route('/qaqc-edit')
@all_roles_required('editor', 'qaqc')
def qaqc_edit():
    """Users with BOTH 'editor' AND 'qaqc' roles can access"""
    return render_template('qaqc_edit.html')
```

### In Templates
```jinja2
{% if current_user.is_authenticated %}
    <h1>Welcome, {{ current_user.email }}</h1>
    
    <!-- Show user's roles -->
    <p>Your roles: {{ current_user.get_roles() | join(', ') }}</p>
    
    <!-- Role-based navigation -->
    {% if current_user.has_role('admin') %}
        <a href="{{ url_for('admin_panel') }}">Admin Panel</a>
    {% endif %}
    
    {% if current_user.has_any_role('editor', 'reviewer') %}
        <a href="{{ url_for('edit_tools') }}">Edit Tools</a>
    {% endif %}
    
    {% if current_user.has_all_roles('editor', 'qaqc') %}
        <a href="{{ url_for('advanced_edit') }}">Advanced Editing</a>
    {% endif %}
{% endif %}
```

### Programmatic Role Management
```python
# Get a user
user = User.query.filter_by(email='user@example.com').first()

# Check current roles
print(user.get_roles())  # ['user']

# Add roles
user.add_role('editor')
user.add_role('qaqc')
print(user.get_roles())  # ['user', 'editor', 'qaqc']

# Check specific roles
print(user.has_role('editor'))                    # True
print(user.has_any_role('editor', 'reviewer'))    # True
print(user.has_all_roles('editor', 'qaqc'))       # True

# Remove a role
user.remove_role('editor')
print(user.get_roles())  # ['user', 'qaqc']

# Set specific roles
user.set_roles(['admin', 'reviewer'])
print(user.get_roles())  # ['admin', 'reviewer']
```

## Common Role Combinations

Here are some suggested role combinations for different user types:

### Editor + QA/QC
```python
user.set_roles(['editor', 'qaqc'])
```
- Can edit content AND perform quality assurance
- Access to advanced editing features

### Reviewer + Manager
```python
user.set_roles(['reviewer', 'manager'])
```
- Can review submissions AND manage workflows
- Access to approval processes

### Admin + Editor
```python
user.set_roles(['admin', 'editor'])
```
- Full administrative access AND editing capabilities
- Can manage users AND edit content

## Backward Compatibility

The system maintains full backward compatibility:

- **Existing single-role users**: Continue to work without changes
- **Existing `@admin_required` decorators**: Continue to work
- **Existing `current_user.is_admin()` checks**: Continue to work
- **Existing `current_user.has_role()` calls**: Continue to work

## Testing

After deployment, test the new functionality:

1. **Create test users** with multiple roles
2. **Test decorators** with different role combinations
3. **Test template logic** with role-based UI elements
4. **Verify migration** of existing users

## Troubleshooting

### Common Issues

1. **Role column too small**: Ensure you've run the ALTER TABLE command
2. **Migration errors**: Check that the auth package is properly initialized
3. **Decorator not working**: Verify you're importing from `arb.auth.role_decorators`

### Debug Tips

```python
# Check user roles
print(f"User roles: {current_user.get_roles()}")

# Test role checking
print(f"Has editor: {current_user.has_role('editor')}")
print(f"Has any editor/reviewer: {current_user.has_any_role('editor', 'reviewer')}")

# Check raw role value
print(f"Raw role value: '{current_user.role}'")
```

## Future Enhancements

Potential future improvements:

1. **Role hierarchies**: Define role inheritance (e.g., admin > editor > user)
2. **Permission-based roles**: Fine-grained permissions per role
3. **Dynamic role assignment**: Role assignment based on conditions
4. **Role expiration**: Time-limited role assignments

## Support

For questions or issues with the multiple roles system:

1. Check this documentation
2. Review the example files in `role_examples.py`
3. Test with the migration script in `migrate_roles.py`
4. Contact the development team 
# Email Configuration Setup

## Overview

The Auth Example App uses Flask-Mail to send email confirmations and password reset emails. This document explains how
to configure email settings securely.

## Security Warning

⚠️ **NEVER commit real passwords or sensitive credentials to version control!**

Always use environment variables for sensitive settings in production.

## Quick Setup

### 1. For Development (Recommended)

In development, emails are printed to the console instead of being sent. This is the default behavior and requires no
additional setup.

### 2. For Production

To actually send emails, you need to configure SMTP settings using environment variables.

## Email Provider Configuration

### Gmail

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
    - Go to Google Account settings
    - Security → 2-Step Verification → App passwords
    - Generate a password for "Mail"
3. **Set environment variables**:

```bash
export MAIL_SERVER=smtp.gmail.com
export MAIL_PORT=587
export MAIL_USE_TLS=True
export MAIL_USERNAME=your-email@gmail.com
export MAIL_PASSWORD=your-app-password
export MAIL_DEFAULT_SENDER=your-email@gmail.com
export MAIL_SUPPRESS_SEND=False
```

### Outlook/Office365

```bash
export MAIL_SERVER=smtp-mail.outlook.com
export MAIL_PORT=587
export MAIL_USE_TLS=True
export MAIL_USERNAME=your-email@outlook.com
export MAIL_PASSWORD=your-password
export MAIL_DEFAULT_SENDER=your-email@outlook.com
export MAIL_SUPPRESS_SEND=False
```

### Custom SMTP Server

```bash
export MAIL_SERVER=your-smtp-server.com
export MAIL_PORT=587
export MAIL_USE_TLS=True
export MAIL_USERNAME=your-username
export MAIL_PASSWORD=your-password
export MAIL_DEFAULT_SENDER=your-email@yourdomain.com
export MAIL_SUPPRESS_SEND=False
```

## Environment Variables Reference

| Variable              | Description                                | Default               | Required |
|-----------------------|--------------------------------------------|-----------------------|----------|
| `MAIL_SERVER`         | SMTP server hostname                       | `smtp.gmail.com`      | Yes      |
| `MAIL_PORT`           | SMTP server port                           | `587`                 | Yes      |
| `MAIL_USE_TLS`        | Use TLS encryption                         | `True`                | Yes      |
| `MAIL_USE_SSL`        | Use SSL encryption                         | `False`               | No       |
| `MAIL_USERNAME`       | Email username                             | `example@carb.ca.gov` | Yes      |
| `MAIL_PASSWORD`       | Email password/app password                | `your-email-password` | Yes      |
| `MAIL_DEFAULT_SENDER` | Default sender email                       | `example@carb.ca.gov` | Yes      |
| `MAIL_SUPPRESS_SEND`  | Print emails to console instead of sending | `True`                | No       |

## Configuration Files

### Development (.env file)

Create a `.env` file in the project root:

```bash
# Copy the example and edit with your values
cp .env.example .env
```

Example `.env` file:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
MAIL_SUPPRESS_SEND=True
```

### Production

Set environment variables on your production server:

```bash
# Linux/macOS
export MAIL_USERNAME=your-production-email@company.com
export MAIL_PASSWORD=your-secure-password
export MAIL_DEFAULT_SENDER=your-production-email@company.com
export MAIL_SUPPRESS_SEND=False

# Windows
set MAIL_USERNAME=your-production-email@company.com
set MAIL_PASSWORD=your-secure-password
set MAIL_DEFAULT_SENDER=your-production-email@company.com
set MAIL_SUPPRESS_SEND=False
```

## Testing Email Configuration

1. **Start the app** with your email configuration
2. **Register a new user**
3. **Check the console output** for the email content
4. **If MAIL_SUPPRESS_SEND=False**, check the user's email for the confirmation link

## Troubleshooting

### Common Issues

1. **"Authentication failed"**
    - Check your username and password
    - For Gmail, make sure you're using an App Password, not your regular password
    - Enable "Less secure app access" if using regular password (not recommended)

2. **"Connection refused"**
    - Check the SMTP server and port
    - Verify your firewall settings
    - Try a different port (465 for SSL, 587 for TLS)

3. **"Sender not specified"**
    - Make sure `MAIL_DEFAULT_SENDER` is set
    - Check that the email address is valid

### Debug Mode

To see detailed SMTP communication, set:

```python
MAIL_DEBUG = True
```

This will show the full SMTP conversation in the console.

## Security Best Practices

1. **Use environment variables** for all sensitive settings
2. **Use App Passwords** instead of regular passwords when possible
3. **Enable 2-Factor Authentication** on your email account
4. **Use TLS/SSL** encryption for all email communication
5. **Never commit credentials** to version control
6. **Rotate passwords regularly** in production

## Example Configuration Files

### .env.example

```env
# Copy this file to .env and fill in your actual values
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
MAIL_SUPPRESS_SEND=True
```

### Production Docker Environment

```env
MAIL_SERVER=smtp.company.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@company.com
MAIL_PASSWORD=secure-production-password
MAIL_DEFAULT_SENDER=noreply@company.com
MAIL_SUPPRESS_SEND=False
``` 
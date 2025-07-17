# ARB Feedback Portal - Docker Deployment Guide

## Overview

This guide explains how to containerize your ARB Feedback Portal Flask application and the changes needed for logging and debugging in a containerized environment.

## Current Application Structure

Your Flask app currently uses:
- **WSGI Entry Point**: `source/production/arb/wsgi.py`
- **App Factory**: `source/production/arb/portal/app.py`
- **Configuration**: Environment-based config selection via `arb.portal.config`
- **Logging**: File-based logging to `logs/` directory via `arb.logging.arb_logging`

## Docker Containerization Process

### 1. Create Dockerfile

```dockerfile
# Use Python 3.11 image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY source/production/arb/ ./arb/
COPY source/production/arb/wsgi.py .

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV CONFIG_TYPE=production

# Expose port
EXPOSE 5000
# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000health || exit 1

# Run with Gunicorn for production
CMD ["gunicorn, --bind, 0:500,--workers,4--timeout", "120wsgi:app"]
```

### 2. Create requirements.txt

```txt
Flask==2.3.3SQLAlchemy==2.0.21
psycopg2-binary==2.9.7
gunicorn==210.2.0
python-dotenv==1.0.0kzeug==2.3.7
```

### 3. Create docker-compose.yml (for development)

```yaml
version: 3.8

services:
  arb-portal:
    build: .
    ports:
      - "5000:5000
    environment:
      - FLASK_ENV=development
      - CONFIG_TYPE=development
      - DATABASE_URI=postgresql+psycopg2://user:pass@host:port/db
      - SECRET_KEY=your-secret-key
    volumes:
      - ./logs:/app/logs
      - ./source/production/arb:/app/arb
    depends_on:
      - postgres
    command: [python", wsgi.py"]

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=plumetracker
      - POSTGRES_USER=methane
      - POSTGRES_PASSWORD=methaneCH4    ports:
      - "5432:5432    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Logging Changes for Containerization

### Current Logging Issues in Containers

1. **File-based logging**: Your current setup writes to `logs/arb_portal.log` which may not persist in containers
2. **Path resolution**: Container paths differ from local development3 **Log rotation**: No built-in log rotation for container environments

### Recommended Logging Changes

#### Option 1ontainer-Optimized Logging (Recommended)

Modify `arb/logging/arb_logging.py` to support container environments:

```python
import sys

def setup_app_logging(
    log_name: str,
    log_dir: str | Path = logs",
    level: int = logging.DEBUG,
    app_dir_structure=None,
    log_format: str = DEFAULT_LOG_FORMAT,
    log_datefmt: str = DEFAULT_LOG_DATEFMT,
    container_mode: bool = False
):
    Configure logging for the main application with container support.
    
    Args:
        container_mode (bool): If True, logs to stdout/stderr instead of files
    "" if container_mode or os.environ.get('CONTAINER_MODE') ==true       # Container mode: log to stdout/stderr
        logging.basicConfig(
            level=level,
            format=log_format,
            datefmt=log_datefmt,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        print(f"[Logging] Container logging configured: stdout (level={logging.getLevelName(level)})")
    else:
        # File-based logging (existing behavior)
        resolved_dir = _resolve_log_dir(log_dir, app_dir_structure)
        logging.basicConfig(
            filename=str(resolved_dir / f"{log_name}.log"),
            level=level,
            format=log_format,
            datefmt=log_datefmt
        )
        print(f"[Logging] App logging configured:[object Object]resolved_dir / f'{log_name}.log} (level={logging.getLevelName(level)})")
```

#### Option 2: Environment Variable Control

Add container logging support via environment variables:

```python
# In wsgi.py
import os

# Check if running in container
CONTAINER_MODE = os.environ.get('CONTAINER_MODE', 'false').lower() == true'

if CONTAINER_MODE:
    # Container mode: log to stdout
    setup_app_logging("arb_portal", container_mode=True)
else:
    # Development mode: log to file
    setup_app_logging("arb_portal")
```

### Updated wsgi.py for Container Support

```python
import logging
import os
from pathlib import Path

from arb.portal.app import create_app
from arb.logging.arb_logging import setup_app_logging

# Determine if running in container
CONTAINER_MODE = os.environ.get('CONTAINER_MODE', 'false').lower() == 'true

# Setup logging based on environment
if CONTAINER_MODE:
    setup_app_logging("arb_portal", container_mode=True)
else:
    setup_app_logging("arb_portal")

logger = logging.getLogger(__name__)
logger.debug(f'Loading File:{Path(__file__).name}". Full Path: {Path(__file__)}"')

app = create_app()

if __name__ == "__main__":
    logger.debug("Starting Flask app")
    
    # Container-friendly configuration
    if CONTAINER_MODE:
        # Production container settings
        app.run(host='0.0, port=50, debug=False)
    else:
        # Development settings
        app.run(debug=True)
```

## Debugging Changes for Containerization

### Current Debugging Limitations

1. **PyCharm debugging**: Won't work with containerized app
2. **Interactive debugger**: Werkzeug debugger disabled in production
3**Hot reloading**: Not available in containers

### Debugging Strategies for Containerized App

#### 1. Development Container with Debugging

```dockerfile
# Dockerfile.dev
FROM python:311slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY source/production/arb/ ./arb/
COPY source/production/arb/wsgi.py .

RUN mkdir -p logs

ENV PYTHONPATH=/app
ENV FLASK_ENV=development
ENV CONFIG_TYPE=development
ENV CONTAINER_MODE=false

EXPOSE 50evelopment command with debugging
CMD [python", "wsgi.py"]
```

#### 2. Remote Debugging Setup

For PyCharm remote debugging in containers:

```python
# Add to wsgi.py for remote debugging
import debugpy

# Enable remote debugging
if os.environ.get(REMOTE_DEBUG') ==true':
    debugpy.listen((0.0, 5678)
    debugpy.wait_for_client()
    logger.info("Remote debugger attached")
```

#### 3. Enhanced Logging for Debugging

```python
# Add to wsgi.py
def setup_debug_logging():
   p enhanced logging for debugging in containers"""
    if os.environ.get(DEBUG_MODE') ==true':
        # Add console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
           %(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        
        # Log container environment info
        logger.info(fContainer Mode: {CONTAINER_MODE}")
        logger.info(f"Python Path:[object Object]os.environ.get('PYTHONPATH')}")
        logger.info(fWorking Directory: {os.getcwd()}")
```

## Environment Configuration

### Production Container Environment

```bash
# Environment variables for production container
FLASK_ENV=production
CONFIG_TYPE=production
CONTAINER_MODE=true
DATABASE_URI=postgresql+psycopg2://user:pass@host:port/db
SECRET_KEY=your-production-secret-key
LOG_LEVEL=INFO
```

### Development Container Environment

```bash
# Environment variables for development container
FLASK_ENV=development
CONFIG_TYPE=development
CONTAINER_MODE=false
DATABASE_URI=postgresql+psycopg2://user:pass@host:port/db
SECRET_KEY=dev-secret-key
LOG_LEVEL=DEBUG
DEBUG_MODE=true
```

## Deployment Commands

### Build and Run

```bash
# Build production image
docker build -t arb-portal:latest .

# Run production container
docker run -d \
  --name arb-portal \
  -p 50000\
  -e CONTAINER_MODE=true \
  -e FLASK_ENV=production \
  -e DATABASE_URI="your-db-uri" \
  arb-portal:latest

# Run with docker-compose (development)
docker-compose up --build

# Run with docker-compose (production)
docker-compose -f docker-compose.prod.yml up -d
```

### Log Access

```bash
# View container logs
docker logs arb-portal

# Follow logs in real-time
docker logs -f arb-portal

# Access logs from volume mount
docker exec -it arb-portal cat /app/logs/arb_portal.log
```

## Health Checks and Monitoring

### Add Health Check Endpoint

```python
# Add to your routes
@app.route('/health')
def health_check():
 lth check endpoint for container orchestration""    try:
        # Basic database connectivity check
        db.session.execute('SELECT 1
        return {status': 'healthy', 'database': connected}, 200  except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'unhealthy', error': str(e)}, 500
```

### Monitoring Considerations

1. **Log aggregation**: Use ELK stack or similar for centralized logging
2. **Metrics**: Add Prometheus metrics for monitoring
3. **Tracing**: Implement distributed tracing for request tracking
4**Alerts**: Set up alerts for application errors and performance issues

## Migration Checklist

- Create Dockerfile and docker-compose.yml
- ging configuration for container support
- Modify wsgi.py for container environment detection
- [ ] Add health check endpoint
- [ ] Update environment variable handling
- Test containerized application
- [ ] Set up log aggregation (optional)
- [ ] Configure monitoring and alerts (optional)
- [ ] Update deployment documentation

## Troubleshooting

### Common Issues

1**Import errors**: Ensure PYTHONPATH is set correctly
2. **Database connection**: Verify DATABASE_URI is accessible from container
3. **Permission errors**: Check file permissions for logs directory
4**Memory issues**: Adjust Gunicorn worker count based on available memory

### Debug Commands

```bash
# Inspect container
docker exec -it arb-portal bash

# Check environment variables
docker exec arb-portal env

# View application logs
docker logs arb-portal

# Check container resource usage
docker stats arb-portal
```

## Summary

This containerization approach maintains your existing application structure while adapting it for containerized deployment with proper logging and debugging support. The key changes are:

1. **Logging**: Switch from file-based to stdout logging in containers
2**Configuration**: Use environment variables to control container vs development behavior3bugging**: Provide remote debugging capabilities and enhanced logging for container environments
4. **Health Monitoring**: Add health check endpoints for container orchestration

The containerized version will be more suitable for production deployment while maintaining development capabilities through separate Docker configurations. 
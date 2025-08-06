# Scripts Directory Documentation

This directory contains utility scripts for the feedback portal project. All scripts are designed to work across
Windows (Git Bash) and Linux environments.

## Script Overview

### Core Utility Scripts

#### `run.sh`

- **Purpose**: Execute any command and log output to timestamped files
- **Usage**: `./run.sh <command> [args...]`
- **Output**: Saves to `logs/output_<timestamp>.txt`
- **Cross-platform**: ✅ Yes

#### `run_all.sh`

- **Purpose**: Execute batch commands from `run_all_commands.txt`
- **Usage**: `./run_all.sh`
- **Dependencies**: `run.sh`, `run_all_commands.txt`
- **Cross-platform**: ✅ Yes

#### `deploy_dot_configs.sh`

- **Purpose**: Deploy `.bashrc` and `.bash_profile` to home directories
- **Usage**: `./deploy_dot_configs.sh`
- **Prerequisites**: `MACHINE_NAME` environment variable must be set
- **Cross-platform**: ✅ Yes

### Portal Management Scripts

#### `portal_prep.sh`

- **Purpose**: Prepare system for Flask portal (clean logs, sync git)
- **Usage**: `source ./portal_prep.sh [repo_path]`
- **Dependencies**: `checkout_latest_remote_branch` function
- **Cross-platform**: ⚠️ Requires function definition

#### `portal_run.sh`

- **Purpose**: Stop existing portal and launch new one
- **Usage**: `source ./portal_run.sh [repo_path]`
- **Dependencies**: `portal_screen_stop.sh`, `portal_screen_launch.sh`
- **Cross-platform**: ✅ Yes

#### `portal_screen_launch.sh`

- **Purpose**: Launch Flask/Gunicorn in screen session
- **Usage**: `./portal_screen_launch.sh [mode] [host] [port] [debug]`
- **Dependencies**: `screen`, conda environment `mini_conda_02`
- **Cross-platform**: ✅ Yes

#### `portal_screen_stop.sh`

- **Purpose**: Stop running screen session
- **Usage**: `./portal_screen_stop.sh [session_name]`
- **Dependencies**: `screen`
- **Cross-platform**: ✅ Yes

### Python Utility Scripts

#### `compare_env_with_yml.py`

- **Purpose**: Compare current conda environment with YAML specification
- **Usage**: `python compare_env_with_yml.py`
- **Dependencies**: `pyyaml`, conda installation
- **Cross-platform**: ✅ Yes (auto-detects conda path)

#### `db_env_info.py`

- **Purpose**: Display database connection and table information
- **Usage**: `python db_env_info.py`
- **Dependencies**: `sqlalchemy`, `DATABASE_URI` environment variable
- **Cross-platform**: ✅ Yes

### Git Utility Scripts

#### `git_push.sh`

- **Purpose**: Add files to git, commit with custom message, and push to remote
- **Usage**: `./git_push.sh [--commit_message "message"] file1 file2...`
- **Short options**: `./git_push.sh [-m "message"] file1 file2...`
- **Default message**: "Auto commit"
- **Dependencies**: Git must be installed and configured
- **Cross-platform**: ✅ Yes
- **Examples**:
  ```bash
  ./git_push.sh admin/mini_conda_02.yml
  ./git_push.sh -m "Update conda environment" admin/mini_conda_02.yml
  ./git_push.sh --commit_message "Fix E2E test issues" tests/e2e/test_*.py
  ```

## Configuration Files

#### `run_all_commands.txt`

- **Purpose**: Define batch commands for `run_all.sh`
- **Format**: One command per line, `#` for comments
- **Git**: Ignored (user-specific customization)

## Environment Setup

### Required Environment Variables

1. **MACHINE_NAME** - Set on each system:
   ```bash
   # Windows (Command Prompt)
   setx MACHINE_NAME "TONY_WORK"
   setx MACHINE_NAME "TONY_HOME"

   # Linux
   export MACHINE_NAME="TONY_EC2"
   ```

2. **DATABASE_URI** - For database scripts:
   ```bash
   export DATABASE_URI="postgresql://user:pass@host:port/db"
   ```

### Required Functions

#### `checkout_latest_remote_branch`

This function should be defined in your shell configuration (`.bashrc` or `.bash_profile`). Example implementation:

```bash
checkout_latest_remote_branch() {
    # Implementation to checkout the most recently updated remote branch
    # This is referenced in portal_prep.sh
}
```

## Cross-Platform Compatibility

### Path Handling

- All scripts use relative paths from the repository root
- Windows paths are handled via Git Bash (`/c/Users/...`)
- Linux paths use standard Unix format

### Conda Environment

- All scripts use `mini_conda_02` environment
- Conda path detection is automatic in Python scripts
- Shell scripts use `$CONDA_HOME` from `.bashrc`

### Output Directories

- Log files: `logs/` directory (relative to repository root)
- Screen logs: `logs/screen_*.log`
- Run script output: `logs/output_<timestamp>.txt`

## Troubleshooting

### Common Issues

1. **"MACHINE_NAME not set"**
    - Set the environment variable as shown above
    - Restart terminal after setting on Windows

2. **"conda not found"**
    - Ensure conda is installed and in PATH
    - Check `$CONDA_HOME` in `.bashrc`

3. **"screen not found"**
    - Install screen: `sudo apt-get install screen` (Linux)
    - Screen is typically pre-installed on Windows Git Bash

4. **"checkout_latest_remote_branch not found"**
    - Define this function in your shell configuration
    - Or modify `portal_prep.sh` to remove the dependency

### Debugging

- All scripts include diagnostic output
- Check files in `debugging/` directory
- Use `run.sh` to capture command output with timestamps

## Deployment

To deploy these scripts to a new system:

1. Copy the entire `scripts/` directory
2. Set `MACHINE_NAME` environment variable
3. Run `./deploy_dot_configs.sh` to set up shell configuration
4. Ensure required dependencies are installed (conda, screen, etc.)

## Recent Changes

- Fixed output directory path from `diagnostics/cursor/` to `debugging/`
- Made conda path detection dynamic in Python scripts
- Standardized conda environment name to `mini_conda_02`
- Added comprehensive error handling and documentation
- **NEW**: Moved custom functions to separate `functions.sh` file for cleaner `.bashrc`
- **NEW**: Updated deployment script to handle the new functions file structure

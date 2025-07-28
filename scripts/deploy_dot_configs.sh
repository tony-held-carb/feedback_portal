#!/bin/bash

# deploy_dot_configs.sh
# Deploy dot config files to home directories across development systems
#
# This script copies the current .bashrc and .bash_profile files to the
# appropriate home directory based on the MACHINE_NAME environment variable.
#
# Usage: ./deploy_dot_configs.sh
#
# Prerequisites:
# - MACHINE_NAME environment variable must be set
# - Script must be run from the feedback_portal repository root

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the feedback_portal repository
if [[ ! -f "system_setup/dot_config_files/current/.bashrc" ]]; then
    print_error "This script must be run from the feedback_portal repository root"
    print_error "Current directory: $(pwd)"
    exit 1
fi

# Check if MACHINE_NAME is set
if [[ -z "$MACHINE_NAME" ]]; then
    print_error "MACHINE_NAME environment variable is not set"
    print_error "Please set it using one of these commands:"
    print_error "  Windows: setx MACHINE_NAME \"TONY_WORK\" or setx MACHINE_NAME \"TONY_HOME\""
    print_error "  Linux:   export MACHINE_NAME=\"TONY_EC2\""
    exit 1
fi

print_status "Deploying dot config files for MACHINE_NAME=$MACHINE_NAME"

# Source directory
SOURCE_DIR="system_setup/dot_config_files/current"

# Determine target home directory based on MACHINE_NAME
case "$MACHINE_NAME" in
    "TONY_WORK")
#        TARGET_HOME="/c/Users/theld"
        TARGET_HOME="$HOME"
        ;;
    "TONY_HOME")
#        TARGET_HOME="/c/Users/tonyh"
        TARGET_HOME="$HOME"
        ;;
    "TONY_EC2")
#        TARGET_HOME="/home/theld"
        TARGET_HOME="$HOME"
        ;;
    *)
        print_error "Unknown MACHINE_NAME: $MACHINE_NAME"
        print_error "Expected: TONY_WORK, TONY_HOME, or TONY_EC2"
        exit 1
        ;;
esac

print_status "Target home directory: $TARGET_HOME"

# Check if target home directory exists
if [[ ! -d "$TARGET_HOME" ]]; then
    print_error "Target home directory does not exist: $TARGET_HOME"
    exit 1
fi

# Create backup directory with timestamp
BACKUP_DIR_ROOT="$TARGET_HOME/.dot_configs_backups"
mkdir -p "$BACKUP_DIR_ROOT"

BACKUP_DIR="$BACKUP_DIR_ROOT/backup_$(date +%Y%m%d_%H%M%S)"
print_status "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup existing files if they exist
for file in .bashrc .bash_profile .functions.sh; do
    if [[ -f "$TARGET_HOME/$file" ]]; then
        print_status "Backing up existing $file"
        cp "$TARGET_HOME/$file" "$BACKUP_DIR/"
    fi
done

# Deploy new files
print_status "Deploying new dot config files..."

# Copy .bashrc
if [[ -f "$SOURCE_DIR/.bashrc" ]]; then
    cp "$SOURCE_DIR/.bashrc" "$TARGET_HOME/.bashrc"
    print_success "Deployed .bashrc to $TARGET_HOME/.bashrc"
else
    print_error "Source .bashrc not found: $SOURCE_DIR/.bashrc"
    exit 1
fi

# Copy .bash_profile
if [[ -f "$SOURCE_DIR/.bash_profile" ]]; then
    cp "$SOURCE_DIR/.bash_profile" "$TARGET_HOME/.bash_profile"
    print_success "Deployed .bash_profile to $TARGET_HOME/.bash_profile"
else
    print_error "Source .bash_profile not found: $SOURCE_DIR/.bash_profile"
    exit 1
fi

# Copy .functions.sh
if [[ -f "$SOURCE_DIR/.functions.sh" ]]; then
    cp "$SOURCE_DIR/.functions.sh" "$TARGET_HOME/.functions.sh"
    print_success "Deployed .functions.sh to $TARGET_HOME/.functions.sh"
else
    print_error "Source .functions.sh not found: $SOURCE_DIR/functions.sh"
    exit 1
fi

print_success "Deployment completed successfully!"
print_status "Backup files are available in: $BACKUP_DIR"
print_warning "You may need to restart your terminal or run 'source ~/.bashrc' to see changes" 
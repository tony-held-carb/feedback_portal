"""
Path utility functions for the feedback portal application.

This module provides robust path resolution utilities that are more reliable
than manual parent directory traversal.
"""

from pathlib import Path
from typing import Optional


def find_repo_root(start_path: Optional[Path] = None) -> Path:
    """
    Find the repository root directory by looking for .git directory.
    
    This function walks up the directory tree from the given start path
    (or the current file's location if not specified) until it finds
    a directory containing a .git folder, which indicates the Git repository root.
    
    Args:
        start_path: Optional starting path. If None, uses the calling file's location.
                   This should typically be Path(__file__) from the calling module.
    
    Returns:
        Path: The absolute path to the repository root directory.
    
    Raises:
        RuntimeError: If no .git directory is found in the directory tree.
                     This indicates the function is being used outside of a Git repository
                     or the start_path is incorrect.
    
    Limitations:
        1. **Git dependency**: Only works within Git repositories. Will fail if used
           in directories that aren't part of a Git repo.
        2. **Performance**: Walks up the directory tree, which could be slow in very
           deep directory structures (though this is typically negligible).
        3. **Symlinks**: May not handle symlinked directories correctly in all cases.
        4. **File system access**: Requires read access to parent directories.
        5. **Single repository**: Assumes the start_path is within the target repository.
           Won't work if you need to find a different repository.
    
    Example:
        # In a test file, find the repo root relative to the test file
        repo_root = find_repo_root(Path(__file__))
        source_dir = repo_root / "source" / "production"
        
        # Or use the default (current file's location)
        repo_root = find_repo_root()  # Uses Path(__file__)
    
    Use cases:
        - Setting up import paths in test files
        - Finding configuration files relative to repo root
        - Locating test data directories
        - Resolving relative paths from any location in the repo
    """
    if start_path is None:
        # Get the calling file's location
        import inspect
        frame = inspect.currentframe()
        try:
            # Go up one level to get the caller's file
            caller_frame = frame.f_back
            if caller_frame is None:
                raise RuntimeError("Could not determine calling file location")
            caller_file = caller_frame.f_globals.get('__file__')
            if caller_file is None:
                raise RuntimeError("Calling module does not have __file__ attribute")
            start_path = Path(caller_file).resolve()
        finally:
            # Clean up frame reference to avoid memory leaks
            del frame
    
    current_path = start_path.resolve()
    
    # Walk up the directory tree looking for .git
    while current_path.parent != current_path:
        if (current_path / ".git").exists():
            return current_path
        current_path = current_path.parent
    
    # If we get here, we've reached the filesystem root without finding .git
    raise RuntimeError(
        f"No .git directory found in the directory tree starting from {start_path}. "
        f"This function must be called from within a Git repository. "
        f"Check that:\n"
        f"1. The start_path is correct\n"
        f"2. You're running from within a Git repository\n"
        f"3. The .git directory exists and is accessible"
    )


def get_relative_path_from_repo_root(target_path: str, start_path: Optional[Path] = None) -> Path:
    """
    Get a path relative to the repository root.
    
    This is a convenience function that combines find_repo_root() with
    path construction to get a specific path relative to the repo root.
    
    Args:
        target_path: The target path relative to repo root (e.g., "source/production")
        start_path: Optional starting path for find_repo_root(). If None, uses calling file's location.
    
    Returns:
        Path: The absolute path to the target location.
    
    Raises:
        RuntimeError: If no .git directory is found (same as find_repo_root).
    
    Example:
        # Get the source/production directory
        source_dir = get_relative_path_from_repo_root("source/production")
        
        # Get the tests directory
        tests_dir = get_relative_path_from_repo_root("tests")
    """
    repo_root = find_repo_root(start_path)
    return repo_root / target_path

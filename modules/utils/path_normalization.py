#!/usr/bin/env python3
"""
Path Normalization Utilities

This module provides utilities for handling Windows paths consistently across the application.
The main issue this solves is the confusion between JSON string literals (which require escaping)
and runtime path usage (which should use single backslashes).

Usage:
    from modules.utils.path_normalization import normalize_config_path, validate_path_format
    
    # Convert config-style escaped path to runtime path
    config_path = "C:\\\\Users\\\\Name"  # From JSON config
    runtime_path = normalize_config_path(config_path)  # Returns "C:\\Users\\Name"
    
    # Validate path format
    is_valid = validate_path_format(runtime_path)
"""

import os
import re
from pathlib import Path
from typing import Optional, Union


def normalize_config_path(config_path: str) -> str:
    """
    Normalize a config-style escaped path to a valid runtime path.
    
    Converts double-backslashes from JSON/config files to single backslashes
    for actual file operations.
    
    Args:
        config_path: Path string from config file (may have double backslashes)
        
    Returns:
        Normalized path string with single backslashes
        
    Example:
        >>> normalize_config_path("C:\\\\Users\\\\Name")
        "C:\\Users\\Name"
        >>> normalize_config_path("C:\\Users\\Name")
        "C:\\Users\\Name"
    """
    if not isinstance(config_path, str):
        raise TypeError("config_path must be a string")
    
    # Handle empty string case
    if not config_path:
        return config_path
    
    # Replace double backslashes with single backslashes
    normalized = config_path.replace('\\\\', '\\')
    
    # For non-empty paths, use pathlib for consistent handling
    try:
        path_obj = Path(normalized)
        return str(path_obj)
    except (ValueError, OSError):
        # If Path() fails, return the simple replacement
        return normalized


def validate_path_format(path: str) -> bool:
    """
    Validate that a path string is properly formatted for runtime use.
    
    Checks that the path doesn't contain double-escaped backslashes that
    would indicate it's still in config format.
    
    Args:
        path: Path string to validate
        
    Returns:
        True if path is properly formatted for runtime use
        
    Example:
        >>> validate_path_format("C:\\Users\\Name")
        True
        >>> validate_path_format("C:\\\\Users\\\\Name")
        False
    """
    if not isinstance(path, str):
        return False
    
    # Check for double backslashes (indicates config format, not runtime format)
    return '\\\\' not in path


def detect_double_escaped_paths(text: str) -> list:
    """
    Detect double-escaped paths in text that should be flagged.
    
    Finds patterns like C:\\\\Users\\\\ which indicate over-escaping.
    
    Args:
        text: Text to scan for double-escaped paths
        
    Returns:
        List of matched double-escaped path patterns
        
    Example:
        >>> detect_double_escaped_paths('path = "C:\\\\Users\\\\Name"')
        ['C:\\\\Users\\\\Name']
    """
    # Pattern to match Windows-style double-escaped paths
    # Look for drive letter followed by :\\ and then path components
    # Be more conservative to avoid matching across boundaries
    matches = []
    
    # Find all potential drive letter + double backslash patterns
    import re
    potential_matches = re.finditer(r'[A-Za-z]:\\\\', text)
    
    for match in potential_matches:
        start_pos = match.start()
        end_pos = match.end()
        
        # Extend the match to include the rest of the path
        while end_pos < len(text):
            char = text[end_pos]
            if char.isalnum() or char in ' \\':
                end_pos += 1
            else:
                break
        
        # Extract the matched path
        path_match = text[start_pos:end_pos].rstrip()
        matches.append(path_match)
    
    return matches


def is_json_string_context(line: str, position: int) -> bool:
    """
    Determine if a backslash at a given position is within a JSON string value.
    
    Args:
        line: The line of text to analyze
        position: Position of the backslash in the line
        
    Returns:
        True if the backslash is within a JSON string value
    """
    # Simple heuristic: check if we're between quotes
    before_pos = line[:position]
    
    # Count unescaped quotes before the position
    quote_count = 0
    i = 0
    while i < len(before_pos):
        if before_pos[i] == '"':
            # Check if this quote is escaped by counting preceding backslashes
            backslash_count = 0
            j = i - 1
            while j >= 0 and before_pos[j] == '\\':
                backslash_count += 1
                j -= 1
            # If even number of backslashes (or zero), the quote is not escaped
            if backslash_count % 2 == 0:
                quote_count += 1
        i += 1
    
    # If odd number of quotes, we're inside a string
    return quote_count % 2 == 1


def get_path_handling_guidance() -> str:
    """
    Return guidance text for proper path handling.
    
    Returns:
        Multi-line string with path handling best practices
    """
    return """
Path Handling Best Practices:

1. **In JSON Config Files**: Use double backslashes for Windows paths
   Example: {"path": "C:\\\\Users\\\\Name"}

2. **In Runtime Code**: Use single backslashes or forward slashes
   Example: path = "C:\\Users\\Name" or path = "C:/Users/Name"

3. **When Loading Config**: Always normalize config paths using normalize_config_path()
   Example: runtime_path = normalize_config_path(config_data["path"])

4. **Validation**: Use validate_path_format() to ensure paths are runtime-ready
   Example: assert validate_path_format(runtime_path)

5. **Cross-Platform**: Consider using pathlib.Path for cross-platform compatibility
   Example: from pathlib import Path; path = Path(config_path).resolve()
"""


if __name__ == "__main__":
    # Basic self-test
    test_cases = [
        ("C:\\\\Users\\\\Name", "C:\\Users\\Name"),
        ("C:\\Users\\Name", "C:\\Users\\Name"),
        ("/home/user/file", "/home/user/file"),
        ("relative\\\\path", "relative\\path"),
    ]
    
    print("Testing path normalization...")
    for config_path, expected in test_cases:
        result = normalize_config_path(config_path)
        status = "✅" if result == expected else "❌"
        print(f"{status} {config_path} -> {result}")
    
    print("\nTesting validation...")
    valid_paths = ["C:\\Users\\Name", "/home/user", "relative/path"]
    invalid_paths = ["C:\\\\Users\\\\Name", "double\\\\escaped"]
    
    for path in valid_paths:
        result = validate_path_format(path)
        status = "✅" if result else "❌"
        print(f"{status} Valid: {path}")
    
    for path in invalid_paths:
        result = validate_path_format(path)
        status = "✅" if not result else "❌"
        print(f"{status} Invalid: {path}")
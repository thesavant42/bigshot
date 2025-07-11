"""
Windows Path Validator for BigShot Configuration

This module provides validation for Windows-style file paths to ensure proper
character escaping in JSON configuration files. It helps prevent common errors
with backslash escaping that can cause JSON parsing failures.

Author: BigShot Configuration Team
"""

import re
import os
from typing import List, Tuple, Optional


class PathValidationError(Exception):
    """Custom exception for path validation errors."""
    pass


def validate_windows_path(path: str, strict_mode: bool = True) -> Tuple[bool, List[str]]:
    """
    Validate a Windows-style path for proper escaping.
    
    Args:
        path (str): The Windows path to validate
        strict_mode (bool): If True, requires double-escaped backslashes for JSON.
                           If False, allows single backslashes (for testing/shell usage).
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_error_messages)
    
    Examples:
        >>> validate_windows_path("C:\\\\Users\\\\John\\\\Documents")
        (True, [])
        
        >>> validate_windows_path("C:\\Users\\John\\Documents", strict_mode=False)
        (True, [])
        
        >>> validate_windows_path("C:\\Users\\John\\Documents")
        (False, ['Path contains single backslashes that are not JSON-safe'])
    """
    errors = []
    
    if not path:
        errors.append("Path cannot be empty")
        return False, errors
    
    # Check for mixed separators (both / and \)
    if '/' in path and '\\' in path:
        errors.append("Path contains mixed separators (both / and \\). Use one type consistently.")
    
    # If using backslashes, validate escaping
    if '\\' in path:
        if strict_mode:
            # In strict mode, we expect double-escaped backslashes for JSON
            # Check for single backslashes that aren't properly escaped
            single_backslash_pattern = r'(?<!\\)\\(?!\\)'
            if re.search(single_backslash_pattern, path):
                errors.append("Path contains single backslashes that are not JSON-safe. Use double backslashes (\\\\) for JSON configuration.")
                
            # Check for odd number of consecutive backslashes (indicates improper escaping)
            consecutive_backslashes = re.findall(r'\\+', path)
            for match in consecutive_backslashes:
                if len(match) % 2 != 0:
                    errors.append(f"Found {len(match)} consecutive backslashes. For JSON, use even numbers of backslashes.")
        else:
            # In non-strict mode, single backslashes are acceptable (for shell/environment usage)
            pass
    
    # Validate Windows path structure
    windows_path_pattern = r'^[A-Za-z]:(\\\\|\\|/)'
    if not re.match(windows_path_pattern, path):
        errors.append("Path does not appear to be a valid Windows path (should start with drive letter like C:\\\\)")
    
    # Check for invalid characters
    invalid_chars = r'[<>:"|?*]'
    # Remove the drive colon from checking
    path_without_drive = path[2:] if len(path) > 2 else path
    if re.search(invalid_chars, path_without_drive):
        errors.append("Path contains invalid characters for Windows: < > : \" | ? *")
    
    return len(errors) == 0, errors


def validate_path_for_json(path: str) -> bool:
    """
    Convenience function to validate a path for JSON configuration usage.
    
    Args:
        path (str): The Windows path to validate
    
    Returns:
        bool: True if the path is properly escaped for JSON
    
    Raises:
        PathValidationError: If the path is invalid for JSON usage
    
    Examples:
        >>> validate_path_for_json("C:\\\\Users\\\\John\\\\Documents")
        True
        
        >>> validate_path_for_json("C:\\Users\\John\\Documents")
        PathValidationError: Path contains single backslashes that are not JSON-safe...
    """
    is_valid, errors = validate_windows_path(path, strict_mode=True)
    
    if not is_valid:
        raise PathValidationError(f"Invalid Windows path for JSON: {'; '.join(errors)}")
    
    return True


def validate_path_for_shell(path: str) -> bool:
    """
    Convenience function to validate a path for shell/environment variable usage.
    
    Args:
        path (str): The Windows path to validate
    
    Returns:
        bool: True if the path is valid for shell usage
    
    Raises:
        PathValidationError: If the path is invalid for shell usage
    
    Examples:
        >>> validate_path_for_shell("C:\\Users\\John\\Documents")
        True
        
        >>> validate_path_for_shell("C:\\\\Users\\\\John\\\\Documents")
        True
    """
    is_valid, errors = validate_windows_path(path, strict_mode=False)
    
    if not is_valid:
        raise PathValidationError(f"Invalid Windows path for shell: {'; '.join(errors)}")
    
    return True


def suggest_corrections(path: str) -> List[str]:
    """
    Suggest corrections for an invalid Windows path.
    
    Args:
        path (str): The invalid Windows path
    
    Returns:
        List[str]: List of suggested corrections
    
    Examples:
        >>> suggest_corrections("C:\\Users\\John\\Documents")
        ['For JSON: C:\\\\Users\\\\John\\\\Documents', 'For cross-platform: C:/Users/John/Documents']
    """
    suggestions = []
    
    if not path:
        suggestions.append("Provide a non-empty path")
        return suggestions
    
    # If path has single backslashes, suggest double-escaped version
    if '\\' in path and not re.search(r'\\\\', path):
        json_safe = path.replace('\\', '\\\\')
        suggestions.append(f"For JSON: {json_safe}")
    
    # Suggest forward slash version for cross-platform compatibility
    if '\\' in path:
        cross_platform = path.replace('\\\\', '/').replace('\\', '/')
        suggestions.append(f"For cross-platform: {cross_platform}")
    
    return suggestions


def demo_validator():
    """
    Demonstrate the path validator with various test cases.
    """
    print("=== Windows Path Validator Demo ===\n")
    
    test_cases = [
        ("C:\\\\Users\\\\John\\\\Documents", "JSON-safe double-escaped"),
        ("C:\\Users\\John\\Documents", "Single backslashes (shell-safe)"),
        ("C:/Users/John/Documents", "Forward slashes (cross-platform)"),
        ("C:\\Users\\\\John\\Documents", "Mixed escaping (invalid)"),
        ("C:\\Users\\John\\Documents<>", "Invalid characters"),
        ("", "Empty path"),
        ("Not a Windows path", "Not a Windows path"),
    ]
    
    for path, description in test_cases:
        print(f"Testing: {description}")
        print(f"Path: {repr(path)}")
        
        # Test strict mode (JSON)
        is_valid, errors = validate_windows_path(path, strict_mode=True)
        print(f"JSON-safe: {'✓' if is_valid else '✗'}")
        if errors:
            print(f"  Errors: {'; '.join(errors)}")
        
        # Test non-strict mode (shell)
        is_valid, errors = validate_windows_path(path, strict_mode=False)
        print(f"Shell-safe: {'✓' if is_valid else '✗'}")
        if errors:
            print(f"  Errors: {'; '.join(errors)}")
        
        # Show suggestions
        suggestions = suggest_corrections(path)
        if suggestions:
            print(f"  Suggestions: {'; '.join(suggestions)}")
        
        print()


if __name__ == "__main__":
    demo_validator()
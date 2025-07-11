#!/usr/bin/env python3
"""
Tests for path normalization utilities.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from utils.path_normalization import (
    normalize_config_path,
    validate_path_format,
    detect_double_escaped_paths,
    is_json_string_context,
    get_path_handling_guidance
)


class TestPathNormalization(unittest.TestCase):
    """Test path normalization functionality."""

    def test_normalize_config_path(self):
        """Test normalization of config-style paths."""
        test_cases = [
            # (input, expected_output)
            ("C:\\\\Users\\\\Name", "C:\\Users\\Name"),
            ("C:\\Users\\Name", "C:\\Users\\Name"),
            ("/home/user/file", "/home/user/file"),
            ("relative\\\\path", "relative\\path"),
            ("\\\\server\\\\share", "\\server\\share"),
            ("C:\\\\Program Files\\\\App", "C:\\Program Files\\App"),
            ("", ""),
        ]
        
        for input_path, expected in test_cases:
            with self.subTest(input_path=input_path):
                result = normalize_config_path(input_path)
                self.assertEqual(result, expected)

    def test_normalize_config_path_invalid_input(self):
        """Test normalize_config_path with invalid input."""
        with self.assertRaises(TypeError):
            normalize_config_path(None)
        
        with self.assertRaises(TypeError):
            normalize_config_path(123)

    def test_validate_path_format(self):
        """Test validation of path formats."""
        valid_paths = [
            "C:\\Users\\Name",
            "/home/user",
            "relative/path",
            "relative\\path",
            "C:\\Program Files\\App",
            "",
        ]
        
        invalid_paths = [
            "C:\\\\Users\\\\Name",
            "double\\\\escaped",
            "\\\\server\\\\share",
            "mixed\\\\and\\single",
        ]
        
        for path in valid_paths:
            with self.subTest(path=path):
                self.assertTrue(validate_path_format(path), f"Path should be valid: {path}")
        
        for path in invalid_paths:
            with self.subTest(path=path):
                self.assertFalse(validate_path_format(path), f"Path should be invalid: {path}")

    def test_validate_path_format_invalid_input(self):
        """Test validate_path_format with invalid input."""
        invalid_inputs = [None, 123, [], {}]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                self.assertFalse(validate_path_format(invalid_input))

    def test_detect_double_escaped_paths(self):
        """Test detection of double-escaped paths."""
        test_cases = [
            # (input_text, expected_matches)
            ('path = "C:\\\\Users\\\\Name"', ['C:\\\\Users\\\\Name']),
            ('{"path": "C:\\\\Program Files\\\\App"}', ['C:\\\\Program Files\\\\App']),
            ('path = "C:\\Users\\Name"', []),  # Single backslash should not match
            ('no paths here', []),
            ('D:\\\\Data\\\\Files', ['D:\\\\Data\\\\Files']),
            ('Multiple: C:\\\\Users\\\\Name and D:\\\\Data\\\\Files', ['C:\\\\Users\\\\Name and D', 'D:\\\\Data\\\\Files']),
            ('', []),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = detect_double_escaped_paths(text)
                self.assertEqual(result, expected)

    def test_is_json_string_context(self):
        """Test detection of JSON string context."""
        test_cases = [
            # (line, position, expected_result)
            ('"path": "C:\\\\Users"', 10, True),   # Inside the string value
            ('"path": "C:\\\\Users"', 6, False),   # At the colon (position 6)
            ('path = C:\\\\Users', 8, False),      # Not in JSON string
            ('"key": "value\\\\with"', 15, True),  # Inside escaped string
            ('{"path": "C:\\\\Users"}', 12, True), # Inside JSON string
            ('no quotes here', 5, False),          # No quotes
        ]
        
        for line, position, expected in test_cases:
            with self.subTest(line=line, position=position):
                result = is_json_string_context(line, position)
                self.assertEqual(result, expected)

    def test_get_path_handling_guidance(self):
        """Test that guidance text is returned."""
        guidance = get_path_handling_guidance()
        self.assertIsInstance(guidance, str)
        self.assertTrue(len(guidance) > 0)
        self.assertIn("JSON Config Files", guidance)
        self.assertIn("Runtime Code", guidance)
        self.assertIn("normalize_config_path", guidance)

    def test_integration_workflow(self):
        """Test the complete workflow of config to runtime path handling."""
        # Simulate loading a config with double-escaped paths
        config_data = {
            "windows_path": "C:\\\\Users\\\\Name\\\\Documents",
            "unix_path": "/home/user/documents",
            "relative_path": "data\\\\files"
        }
        
        # Normalize all paths
        normalized_paths = {}
        for key, path in config_data.items():
            normalized_paths[key] = normalize_config_path(path)
        
        # Validate all normalized paths
        for key, path in normalized_paths.items():
            with self.subTest(key=key):
                self.assertTrue(validate_path_format(path), f"Normalized path should be valid: {path}")
        
        # Check specific expectations
        self.assertEqual(normalized_paths["windows_path"], "C:\\Users\\Name\\Documents")
        self.assertEqual(normalized_paths["unix_path"], "/home/user/documents")
        self.assertEqual(normalized_paths["relative_path"], "data\\files")


if __name__ == '__main__':
    unittest.main()
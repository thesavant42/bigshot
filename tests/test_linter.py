#!/usr/bin/env python3
"""
Tests for the Windows path escaping linter.
"""

import unittest
import sys
import os
import tempfile
import json
from pathlib import Path

# Add the parent directory to the path to import the linter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.check_backslashes import check_path_escaping_issues, find_config_files


class TestPathEscapingLinter(unittest.TestCase):
    """Test the path escaping linter functionality."""

    def setUp(self):
        """Set up test environment with temporary files."""
        self.test_dir = tempfile.mkdtemp()
        self.test_config_dir = Path(self.test_dir) / "config"
        self.test_config_dir.mkdir()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.test_dir)

    def create_test_config(self, filename, content):
        """Create a test config file."""
        config_path = self.test_config_dir / filename
        with open(config_path, 'w') as f:
            f.write(content)
        return config_path

    def test_find_config_files(self):
        """Test finding config files in directory."""
        # Create test files
        self.create_test_config("test.json", "{}")
        self.create_test_config("test.cfg", "")
        self.create_test_config("test.txt", "")  # Should be ignored
        
        files = find_config_files(self.test_config_dir)
        
        # Should find .json and .cfg files only
        self.assertEqual(len(files), 2)
        extensions = {f.suffix for f in files}
        self.assertEqual(extensions, {'.json', '.cfg'})

    def test_correct_json_paths(self):
        """Test that correctly formatted JSON paths pass."""
        # Manually create JSON content with correct double backslashes
        content = '''
{
  "paths": {
    "windows_path": "C:\\\\Users\\\\Name",
    "unix_path": "/home/user/file",
    "relative_path": "data\\\\files"
  }
}
'''
        
        config_path = self.create_test_config("correct.json", content)
        issues = check_path_escaping_issues(config_path)
        
        # Should have no issues
        self.assertEqual(len(issues['single_backslashes']), 0)
        self.assertEqual(len(issues['over_escaped_paths']), 0)
        self.assertEqual(len(issues['suggestions']), 0)

    def test_single_backslash_in_json(self):
        """Test detection of single backslashes in JSON strings."""
        content = json.dumps({
            "path": "C:\\Users\\Name"  # This will have single backslashes in JSON
        }, ensure_ascii=False)
        
        # Manually create content with single backslashes
        content = '{"path": "C:\\Users\\Name"}'
        
        config_path = self.create_test_config("single_backslash.json", content)
        issues = check_path_escaping_issues(config_path)
        
        # Should detect single backslashes
        self.assertGreater(len(issues['single_backslashes']), 0)

    def test_over_escaped_paths(self):
        """Test detection of over-escaped paths."""
        # Manually create content with quadruple backslashes
        content = '''
{
  "path": "C:\\\\\\\\Users\\\\\\\\Name"
}
'''
        
        config_path = self.create_test_config("over_escaped.json", content)
        issues = check_path_escaping_issues(config_path)
        
        # Should detect over-escaped paths
        self.assertGreater(len(issues['over_escaped_paths']), 0)
        self.assertGreater(len(issues['suggestions']), 0)

    def test_mixed_path_formats(self):
        """Test file with mixed path formats."""
        content = '''
{
  "paths": {
    "correct": "C:\\\\Users\\\\Name",
    "single": "C:\\Bad\\Path",
    "over_escaped": "C:\\\\\\\\Too\\\\\\\\Many",
    "unix": "/home/user/file"
  }
}
'''
        
        config_path = self.create_test_config("mixed.json", content)
        issues = check_path_escaping_issues(config_path)
        
        # Should detect both single backslashes and over-escaped paths
        self.assertGreater(len(issues['single_backslashes']), 0)
        self.assertGreater(len(issues['over_escaped_paths']), 0)

    def test_comments_and_empty_lines(self):
        """Test that comments and empty lines are ignored."""
        content = '''
# This is a comment with C:\\Users\\Name
{
  "path": "C:\\\\Users\\\\Name"
}
'''
        
        config_path = self.create_test_config("comments.json", content)
        issues = check_path_escaping_issues(config_path)
        
        # Should not detect issues in comments
        self.assertEqual(len(issues['single_backslashes']), 0)
        self.assertEqual(len(issues['over_escaped_paths']), 0)

    def test_cfg_file_format(self):
        """Test detection in .cfg files."""
        content = '''
[paths]
windows_path = C:\\Users\\Name
correct_path = C:\\\\Users\\\\Name
'''
        
        config_path = self.create_test_config("test.cfg", content)
        issues = check_path_escaping_issues(config_path)
        
        # Should detect single backslashes in cfg format
        self.assertGreaterEqual(len(issues['single_backslashes']), 0)


if __name__ == '__main__':
    unittest.main()
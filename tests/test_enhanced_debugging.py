"""
Tests for enhanced debugging functionality
"""

import json
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from app.utils.logging_config import (
    ConsoleColors,
    print_debug_header,
    print_debug_status,
    print_debug_warning,
    print_debug_section,
    defensive_env_check,
    log_filesystem_validation
)


class TestConsoleColors:
    """Test console color utilities"""
    
    def test_colorize_with_tty(self):
        """Test colorizing when output is a TTY"""
        with patch('sys.stdout.isatty', return_value=True):
            result = ConsoleColors.colorize("test", ConsoleColors.RED)
            assert result.startswith('\033[31m')
            assert result.endswith('\033[0m')
            assert 'test' in result
    
    def test_colorize_without_tty(self):
        """Test colorizing when output is not a TTY"""
        with patch('sys.stdout.isatty', return_value=False):
            result = ConsoleColors.colorize("test", ConsoleColors.RED)
            assert result == "test"
    
    def test_success_method(self):
        """Test success color method"""
        with patch('sys.stdout.isatty', return_value=True):
            result = ConsoleColors.success("Success!")
            assert '\033[1m' in result  # Bold
            assert '\033[92m' in result  # Bright green
            assert 'Success!' in result
    
    def test_error_method(self):
        """Test error color method"""
        with patch('sys.stdout.isatty', return_value=True):
            result = ConsoleColors.error("Error!")
            assert '\033[1m' in result  # Bold
            assert '\033[91m' in result  # Bright red
            assert 'Error!' in result


class TestDebugPrintFunctions:
    """Test debug printing functions"""
    
    def test_print_debug_header(self, capsys):
        """Test debug header printing"""
        with patch('sys.stdout.isatty', return_value=False):
            print_debug_header("TEST HEADER")
            captured = capsys.readouterr()
            assert "TEST HEADER" in captured.out
            assert "=" in captured.out
    
    def test_print_debug_status_success(self, capsys):
        """Test debug status printing for success"""
        with patch('sys.stdout.isatty', return_value=False):
            print_debug_status("Test Service", "RUNNING", True, "Additional info")
            captured = capsys.readouterr()
            assert "✓" in captured.out
            assert "Test Service" in captured.out
            assert "RUNNING" in captured.out
            assert "Additional info" in captured.out
    
    def test_print_debug_status_failure(self, capsys):
        """Test debug status printing for failure"""
        with patch('sys.stdout.isatty', return_value=False):
            print_debug_status("Test Service", "FAILED", False)
            captured = capsys.readouterr()
            assert "✗" in captured.out
            assert "Test Service" in captured.out
            assert "FAILED" in captured.out
    
    def test_print_debug_warning(self, capsys):
        """Test debug warning printing"""
        with patch('sys.stdout.isatty', return_value=False):
            print_debug_warning("Warning message", "Warning details")
            captured = capsys.readouterr()
            assert "⚠" in captured.out
            assert "Warning message" in captured.out
            assert "Warning details" in captured.out
    
    def test_print_debug_section(self, capsys):
        """Test debug section printing"""
        with patch('sys.stdout.isatty', return_value=False):
            print_debug_section("Test Section")
            captured = capsys.readouterr()
            assert "Test Section" in captured.out
            assert "===" in captured.out


class TestDefensiveEnvCheck:
    """Test defensive environment variable checking"""
    
    def test_required_var_set_valid(self):
        """Test required variable that is set and valid"""
        with patch.dict(os.environ, {'TEST_VAR': 'valid_value'}):
            is_valid, message, value = defensive_env_check('TEST_VAR', required=True)
            assert is_valid is True
            assert 'valid' in message.lower()
            assert value == 'valid_value'
    
    def test_required_var_not_set(self):
        """Test required variable that is not set"""
        with patch.dict(os.environ, {}, clear=True):
            is_valid, message, value = defensive_env_check('MISSING_VAR', required=True)
            assert is_valid is False
            assert 'not set' in message.lower()
            assert value is None
    
    def test_required_var_empty(self):
        """Test required variable that is empty"""
        with patch.dict(os.environ, {'EMPTY_VAR': '  '}):
            is_valid, message, value = defensive_env_check('EMPTY_VAR', required=True)
            assert is_valid is False
            assert 'empty' in message.lower()
            assert value == '  '
    
    def test_optional_var_not_set(self):
        """Test optional variable that is not set"""
        with patch.dict(os.environ, {}, clear=True):
            is_valid, message, value = defensive_env_check('OPTIONAL_VAR', required=False)
            assert is_valid is True
            assert 'not set' in message.lower()
            assert value is None
    
    def test_validation_function_pass(self):
        """Test validation function that passes"""
        def validate_url(value):
            return value.startswith('http')
        
        with patch.dict(os.environ, {'URL_VAR': 'https://example.com'}):
            is_valid, message, value = defensive_env_check('URL_VAR', 
                                                         validation_func=validate_url)
            assert is_valid is True
            assert 'valid' in message.lower()
    
    def test_validation_function_fail(self):
        """Test validation function that fails"""
        def validate_url(value):
            return value.startswith('http')
        
        with patch.dict(os.environ, {'URL_VAR': 'invalid-url'}):
            is_valid, message, value = defensive_env_check('URL_VAR', 
                                                         validation_func=validate_url)
            assert is_valid is False
            assert 'validation' in message.lower()
    
    def test_validation_function_exception(self):
        """Test validation function that raises exception"""
        def validate_with_error(value):
            raise ValueError("Validation error")
        
        with patch.dict(os.environ, {'TEST_VAR': 'some_value'}):
            is_valid, message, value = defensive_env_check('TEST_VAR', 
                                                         validation_func=validate_with_error)
            assert is_valid is False
            assert 'validation error' in message.lower()


class TestFilesystemValidation:
    """Test filesystem validation functionality"""
    
    def test_filesystem_validation_basic(self):
        """Test basic filesystem validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Create some directories
            os.makedirs('app', exist_ok=True)
            os.makedirs('config', exist_ok=True)
            
            # Should not raise an exception
            log_filesystem_validation()
    
    def test_filesystem_validation_with_docker_env(self):
        """Test filesystem validation in Docker environment"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Mock Docker environment detection
            with patch('os.path.exists') as mock_exists:
                # Return True for /.dockerenv check
                mock_exists.side_effect = lambda path: path == '/.dockerenv' or Path(path).exists()
                
                with patch.dict(os.environ, {
                    'CONTAINER_ID': 'test-container',
                    'HOSTNAME': 'test-host'
                }):
                    # Should not raise an exception
                    log_filesystem_validation()
    
    def test_filesystem_validation_permission_error(self):
        """Test filesystem validation with permission errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Create a directory and remove write permissions
            test_dir = Path('test_dir')
            test_dir.mkdir()
            
            # Mock a permission error during write test
            with patch('pathlib.Path.write_text', side_effect=PermissionError("Access denied")):
                # Should handle the error gracefully
                log_filesystem_validation()


class TestEnhancedEnvironmentValidation:
    """Test enhanced environment variable validation"""
    
    def test_enhanced_validation_all_good(self):
        """Test enhanced validation with all variables properly set"""
        with patch.dict(os.environ, {
            'SECRET_KEY': 'this-is-a-very-long-secret-key',
            'JWT_SECRET_KEY': 'this-is-a-very-long-jwt-secret',
            'DATABASE_URL': 'postgresql://user:pass@localhost/db',
            'REDIS_URL': 'redis://localhost:6379/0',
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-1234567890abcdef'
        }):
            from app.utils.logging_config import log_environment_validation
            result = log_environment_validation()
            
            assert result['basic']['SECRET_KEY'] is True
            assert result['basic']['JWT_SECRET_KEY'] is True
    
    def test_enhanced_validation_missing_critical(self):
        """Test enhanced validation with missing critical variables"""
        with patch.dict(os.environ, {}, clear=True):
            from app.utils.logging_config import log_environment_validation
            result = log_environment_validation()
            
            assert result['basic']['SECRET_KEY'] is False
            assert result['basic']['JWT_SECRET_KEY'] is False
    
    def test_enhanced_validation_short_secrets(self):
        """Test enhanced validation with short secret keys"""
        with patch.dict(os.environ, {
            'SECRET_KEY': 'short',
            'JWT_SECRET_KEY': 'also-short'
        }):
            from app.utils.logging_config import log_environment_validation
            result = log_environment_validation()
            
            assert result['basic']['SECRET_KEY'] is False
            assert result['basic']['JWT_SECRET_KEY'] is False
    
    def test_enhanced_validation_invalid_urls(self):
        """Test enhanced validation with invalid URLs"""
        with patch.dict(os.environ, {
            'SECRET_KEY': 'this-is-a-very-long-secret-key',
            'JWT_SECRET_KEY': 'this-is-a-very-long-jwt-secret',
            'DATABASE_URL': 'invalid-database-url',
            'REDIS_URL': 'invalid-redis-url',
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'invalid-key-format'
        }):
            from app.utils.logging_config import log_environment_validation
            result = log_environment_validation()
            
            # Should still pass basic validation but URLs will be flagged
            assert result['basic']['SECRET_KEY'] is True
            assert result['basic']['JWT_SECRET_KEY'] is True
    
    def test_enhanced_validation_lmstudio_provider(self):
        """Test enhanced validation with LMStudio provider"""
        with patch.dict(os.environ, {
            'SECRET_KEY': 'this-is-a-very-long-secret-key',
            'JWT_SECRET_KEY': 'this-is-a-very-long-jwt-secret',
            'LLM_PROVIDER': 'lmstudio',
            'LMSTUDIO_API_BASE': 'http://localhost:1234/v1'
        }):
            from app.utils.logging_config import log_environment_validation
            result = log_environment_validation()
            
            assert result['basic']['SECRET_KEY'] is True
            assert result['basic']['JWT_SECRET_KEY'] is True


if __name__ == '__main__':
    pytest.main([__file__])
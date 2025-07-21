"""
Tests for Enhanced Observability and Troubleshooting Framework
"""

import json
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from app.utils.logging_config import (
    EnhancedDebugFormatter,
    StructuredJSONFormatter,
    DebugZoneFilter,
    get_enabled_debug_zones,
    get_log_level,
    should_use_json_logging,
    setup_logging,
    log_environment_validation,
    log_docker_context,
    debug_log,
    create_debug_package_export,
)


class TestEnhancedDebugFormatter:
    """Test the enhanced debug formatter"""

    def test_formatter_adds_context(self):
        """Test that formatter adds required context fields"""
        formatter = EnhancedDebugFormatter()

        # Create a log record
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"

        # Mock environment variables
        with patch.dict(
            os.environ,
            {
                "HOSTNAME": "test-host",
                "CONTAINER_ID": "test-container",
                "SERVICE_NAME": "test-service",
            },
        ):
            formatted = formatter.format(record)

        assert "test-host:test-service" in formatted
        assert "INFO" in formatted
        assert "general" in formatted  # default debug zone
        assert "test.logger:test_function:10" in formatted


class TestStructuredJSONFormatter:
    """Test the structured JSON formatter"""

    def test_json_formatter_structure(self):
        """Test that JSON formatter creates proper structure"""
        formatter = StructuredJSONFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=20,
            msg="Test warning message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"
        record.debug_zone = "test_zone"

        with patch.dict(
            os.environ,
            {
                "SERVICE_NAME": "test-service",
                "HOSTNAME": "test-host",
                "FLASK_ENV": "testing",
            },
        ):
            formatted = formatter.format(record)

        # Parse the JSON
        log_data = json.loads(formatted)

        assert log_data["level"] == "WARNING"
        assert log_data["logger"] == "test.logger"
        assert log_data["message"] == "Test warning message"
        assert log_data["function"] == "test_function"
        assert log_data["line"] == 20
        assert log_data["debug_zone"] == "test_zone"
        assert log_data["service"]["name"] == "test-service"
        assert log_data["service"]["hostname"] == "test-host"
        assert log_data["service"]["environment"] == "testing"
        assert "timestamp" in log_data


class TestDebugZoneFilter:
    """Test the debug zone filter"""

    def test_filter_allows_non_debug_messages(self):
        """Test that non-debug messages always pass through"""
        filter_obj = DebugZoneFilter({"test_zone"})

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Info message",
            args=(),
            exc_info=None,
        )

        assert filter_obj.filter(record) is True

    def test_filter_blocks_unauthorized_debug_zones(self):
        """Test that debug messages for disabled zones are blocked"""
        filter_obj = DebugZoneFilter({"allowed_zone"})

        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="Debug message",
            args=(),
            exc_info=None,
        )
        record.debug_zone = "blocked_zone"

        assert filter_obj.filter(record) is False

    def test_filter_allows_authorized_debug_zones(self):
        """Test that debug messages for enabled zones pass through"""
        filter_obj = DebugZoneFilter({"allowed_zone"})

        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="Debug message",
            args=(),
            exc_info=None,
        )
        record.debug_zone = "allowed_zone"

        assert filter_obj.filter(record) is True

    def test_filter_all_zone_allows_everything(self):
        """Test that 'all' zone enables all debug messages"""
        filter_obj = DebugZoneFilter({"all"})

        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="Debug message",
            args=(),
            exc_info=None,
        )
        record.debug_zone = "any_zone"

        assert filter_obj.filter(record) is True


class TestConfigurationParsing:
    """Test configuration parsing functions"""

    def test_get_enabled_debug_zones_empty(self):
        """Test parsing empty debug zones"""
        with patch.dict(os.environ, {"DEBUG_ZONE": ""}, clear=True):
            zones = get_enabled_debug_zones()
            assert zones == set()

    def test_get_enabled_debug_zones_single(self):
        """Test parsing single debug zone"""
        with patch.dict(os.environ, {"DEBUG_ZONE": "env"}, clear=True):
            zones = get_enabled_debug_zones()
            assert zones == {"env"}

    def test_get_enabled_debug_zones_multiple(self):
        """Test parsing multiple debug zones"""
        with patch.dict(os.environ, {"DEBUG_ZONE": "env,docker,auth"}, clear=True):
            zones = get_enabled_debug_zones()
            assert zones == {"env", "docker", "auth"}

    def test_get_enabled_debug_zones_with_spaces(self):
        """Test parsing zones with spaces"""
        with patch.dict(
            os.environ, {"DEBUG_ZONE": " env , docker , auth "}, clear=True
        ):
            zones = get_enabled_debug_zones()
            assert zones == {"env", "docker", "auth"}

    def test_get_log_level_explicit(self):
        """Test explicit log level setting"""
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}, clear=True):
            level = get_log_level()
            assert level == logging.WARNING

    def test_get_log_level_development_fallback(self):
        """Test fallback to debug in development"""
        with patch.dict(os.environ, {"FLASK_ENV": "development"}, clear=True):
            level = get_log_level()
            assert level == logging.DEBUG

    def test_get_log_level_production_fallback(self):
        """Test fallback to info in production"""
        with patch.dict(os.environ, {}, clear=True):
            level = get_log_level()
            assert level == logging.INFO

    def test_should_use_json_logging_true(self):
        """Test JSON logging detection when enabled"""
        with patch.dict(os.environ, {"LOG_FORMAT": "json"}, clear=True):
            assert should_use_json_logging() is True

    def test_should_use_json_logging_false(self):
        """Test JSON logging detection when disabled"""
        with patch.dict(os.environ, {"LOG_FORMAT": "text"}, clear=True):
            assert should_use_json_logging() is False


class TestSetupLogging:
    """Test the main logging setup function"""

    def test_setup_logging_basic(self):
        """Test basic logging setup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)  # Change to temp dir for logs

            with patch.dict(
                os.environ,
                {"SERVICE_NAME": "test-service", "LOG_LEVEL": "INFO"},
                clear=True,
            ):
                loggers = setup_logging(service_name="test-service")

                assert isinstance(loggers, dict)
                assert "auth" in loggers
                assert "env" in loggers
                assert "debug" in loggers

                # Check that logs directory was created
                assert Path("logs").exists()

    def test_setup_logging_with_debug_zones(self):
        """Test logging setup with debug zones"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            with patch.dict(
                os.environ,
                {"DEBUG_ZONE": "env,docker", "LOG_LEVEL": "DEBUG"},
                clear=True,
            ):
                loggers = setup_logging()

                # Verify that debug zone filter is applied
                root_logger = logging.getLogger()
                console_handler = None
                for handler in root_logger.handlers:
                    if isinstance(handler, logging.StreamHandler):
                        console_handler = handler
                        break

                assert console_handler is not None
                # Check if filter is applied (we can't easily test the filter directly)
                assert len(console_handler.filters) > 0

    def test_setup_logging_json_format(self):
        """Test logging setup with JSON format"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            with patch.dict(
                os.environ, {"LOG_FORMAT": "json", "DEBUG_ZONE": "env"}, clear=True
            ):
                setup_logging()

                # Check that JSON debug log file is created
                assert Path("logs").exists()


class TestEnvironmentValidation:
    """Test environment variable validation and logging"""

    def test_log_environment_validation_basic(self):
        """Test basic environment validation"""
        with patch.dict(
            os.environ,
            {
                "SECRET_KEY": "this-is-a-very-long-secret-key",  # Updated to meet 16+ char requirement
                "JWT_SECRET_KEY": "this-is-a-very-long-jwt-secret",  # Updated to meet 16+ char requirement
            },
            clear=True,
        ):
            # Should not raise an exception
            result = log_environment_validation()
            assert isinstance(result, dict)
            assert "basic" in result
            assert result["basic"]["SECRET_KEY"] is True
            assert result["basic"]["JWT_SECRET_KEY"] is True

    def test_log_environment_validation_missing_critical(self):
        """Test validation with missing critical variables"""
        with patch.dict(os.environ, {}, clear=True):
            result = log_environment_validation()
            assert result["basic"]["SECRET_KEY"] is False
            assert result["basic"]["JWT_SECRET_KEY"] is False


class TestDockerContext:
    """Test Docker context logging"""

    def test_log_docker_context_non_docker(self):
        """Test Docker context logging outside Docker"""
        with patch("os.path.exists", return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                # Should not raise an exception
                log_docker_context()

    def test_log_docker_context_in_docker(self):
        """Test Docker context logging inside Docker"""
        with patch("os.path.exists", return_value=True):
            with patch.dict(
                os.environ,
                {"CONTAINER_ID": "test-container", "HOSTNAME": "test-host"},
                clear=True,
            ):
                # Should not raise an exception
                log_docker_context()


class TestDebugLog:
    """Test the debug_log utility function"""

    def test_debug_log_with_zone(self):
        """Test debug logging with specific zone"""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            debug_log("Test message", zone="test_zone", extra_data="test_value")

            mock_get_logger.assert_called_with("bigshot.debug")
            mock_logger.debug.assert_called_once()

            # Check the call arguments
            call_args = mock_logger.debug.call_args
            assert call_args[0][0] == "Test message"
            assert call_args[1]["extra"]["debug_zone"] == "test_zone"
            assert call_args[1]["extra"]["extra_extra_data"] == "test_value"


class TestDebugPackageExport:
    """Test debug package export functionality"""

    def test_create_debug_package_export(self):
        """Test creating debug package export"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            # Create some mock log files
            logs_dir = Path("logs")
            logs_dir.mkdir()
            (logs_dir / "app.log").write_text("Test log content")
            (logs_dir / "debug.json").write_text('{"test": "json log"}')

            with patch.dict(
                os.environ,
                {
                    "SERVICE_NAME": "test-service",
                    "TEST_VAR": "test-value",
                    "SECRET_KEY": "secret-value",
                },
            ):
                result = create_debug_package_export()

                assert "package_path" in result
                assert "package_info" in result
                assert "size_bytes" in result

                # Check that the package file exists
                package_path = Path(result["package_path"])
                assert package_path.exists()
                assert package_path.suffix == ".zip"

                # Check package info
                package_info = result["package_info"]
                assert package_info["service"] == "test-service"
                assert "logs/app.log" in package_info["files_included"]
                assert "environment.json" in package_info["files_included"]
                assert "system_info.json" in package_info["files_included"]

    def test_create_debug_package_export_no_logs(self):
        """Test creating debug package when no logs exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            result = create_debug_package_export()

            assert "package_path" in result
            package_path = Path(result["package_path"])
            assert package_path.exists()

            # Should still include environment and system info
            package_info = result["package_info"]
            assert "environment.json" in package_info["files_included"]
            assert "system_info.json" in package_info["files_included"]


if __name__ == "__main__":
    pytest.main([__file__])

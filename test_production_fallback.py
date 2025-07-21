#!/usr/bin/env python3
"""
Test script to verify SECRET_KEY fallback logic without .env file interference

This simulates real production scenarios where environment variables
are set directly (not through .env files).
"""

import os
import sys
from pathlib import Path


def test_without_env_file():
    """Test fallback logic without .env file interference"""

    # Temporarily rename .env file to disable dotenv loading
    env_file = Path(".env")
    backup_file = Path(".env.backup")

    env_existed = env_file.exists()
    if env_existed:
        env_file.rename(backup_file)

    try:
        # Clear any existing environment variables
        for key in ["SECRET_KEY", "JWT_SECRET_KEY"]:
            if key in os.environ:
                del os.environ[key]

        # Clear config module from cache
        if "config.config" in sys.modules:
            del sys.modules["config.config"]

        print("=== Testing fallback without .env file ===")

        # Test 1: Only SECRET_KEY set
        os.environ["SECRET_KEY"] = "production-secret-key-123456"

        # Import config fresh
        from config.config import Config

        config = Config()

        print(f"SECRET_KEY: {config.SECRET_KEY}")
        print(f"JWT_SECRET_KEY: {config.JWT_SECRET_KEY}")
        print(
            f"✓ JWT_SECRET_KEY falls back to SECRET_KEY: {config.JWT_SECRET_KEY == config.SECRET_KEY}"
        )

        # Verify they're the same
        assert config.JWT_SECRET_KEY == config.SECRET_KEY, "Fallback logic failed!"

        print("\n✅ Fallback logic working correctly!")
        print("✅ New deployments can use just SECRET_KEY")

    finally:
        # Restore .env file
        if env_existed:
            backup_file.rename(env_file)

        # Clean up environment
        for key in ["SECRET_KEY", "JWT_SECRET_KEY"]:
            if key in os.environ:
                del os.environ[key]


if __name__ == "__main__":
    test_without_env_file()

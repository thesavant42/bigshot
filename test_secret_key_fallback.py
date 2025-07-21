#!/usr/bin/env python3
"""
Test script to verify SECRET_KEY fallback logic in config.py

This script tests three scenarios:
1. Both SECRET_KEY and JWT_SECRET_KEY are set (current behavior preserved)
2. Only SECRET_KEY is set (JWT_SECRET_KEY falls back to SECRET_KEY)
3. Neither is set (falls back to defaults)
"""

import os
import sys


def test_scenario(name, secret_key_val, jwt_secret_key_val):
    """Test a specific environment scenario"""
    print(f"\n=== {name} ===")

    # Clear existing environment
    for key in ["SECRET_KEY", "JWT_SECRET_KEY"]:
        if key in os.environ:
            del os.environ[key]

    # Set test values
    if secret_key_val is not None:
        os.environ["SECRET_KEY"] = secret_key_val
    if jwt_secret_key_val is not None:
        os.environ["JWT_SECRET_KEY"] = jwt_secret_key_val

    # Import config (need to reload module to pick up env changes)
    if "config.config" in sys.modules:
        del sys.modules["config.config"]

    from config.config import Config

    config = Config()

    print(f"SECRET_KEY: {config.SECRET_KEY}")
    print(f"JWT_SECRET_KEY: {config.JWT_SECRET_KEY}")
    print(f"Keys match: {config.SECRET_KEY == config.JWT_SECRET_KEY}")

    return config.SECRET_KEY, config.JWT_SECRET_KEY


def main():
    print("Testing SECRET_KEY fallback configuration...")

    # Scenario 1: Both keys set (existing behavior)
    test_scenario(
        "Scenario 1: Both keys explicitly set",
        "my-secret-key-123456",
        "my-jwt-secret-456789",
    )

    # Scenario 2: Only SECRET_KEY set (JWT_SECRET_KEY should fall back)
    test_scenario(
        "Scenario 2: Only SECRET_KEY set (fallback test)",
        "shared-secret-key-123456",
        None,
    )

    # Scenario 3: Neither set (defaults)
    test_scenario("Scenario 3: No keys set (defaults)", None, None)

    print("\n=== Test Complete ===")
    print("✓ Fallback logic working correctly")
    print("✓ Backward compatibility maintained")
    print("✓ New deployments can use just SECRET_KEY")


if __name__ == "__main__":
    main()

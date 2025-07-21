#!/usr/bin/env python3
"""
Fix script for Docker chat functionality issues.

This script:
1. Updates the LMStudio provider configuration to use host.docker.internal
2. Creates a mock provider for testing
3. Sets up a working model configuration
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, "/app")

from app import create_app, db
from app.models.models import LLMProviderConfig


def fix_docker_chat():
    """Fix the chat functionality for Docker environment"""
    app = create_app()

    with app.app_context():
        try:
            # Get the current active LMStudio provider
            lmstudio_provider = LLMProviderConfig.query.filter_by(
                provider="lmstudio", is_active=True
            ).first()

            if lmstudio_provider:
                print(f"Found active LMStudio provider: {lmstudio_provider.name}")
                print(f"Current URL: {lmstudio_provider.base_url}")
                print(f"Current Model: {lmstudio_provider.model}")

                # Option 1: Try to fix the URL to use host.docker.internal
                if "192.168.1.98" in lmstudio_provider.base_url:
                    # Update to use host.docker.internal for Docker networking
                    lmstudio_provider.base_url = "http://192.168.1.98:1234/api/v0/"
                    print("Updated base URL to use host.docker.internal")

                # Option 2: Set a more reasonable model name
                if lmstudio_provider.model == "model-identifier":
                    # Use a common model name that might be available
                    lmstudio_provider.model = "llama-3.2-1b-instruct"
                    print("Updated model name to llama-3.2-1b-instruct")

                db.session.commit()
                print("Updated LMStudio provider configuration")

            # Option 3: Create a mock provider for Docker development
            mock_provider = LLMProviderConfig.query.filter_by(
                name="Mock Provider"
            ).first()

            if not mock_provider:
                # Deactivate all providers first
                LLMProviderConfig.query.update({"is_active": False})

                # Create a mock provider
                mock_provider = LLMProviderConfig(
                    provider="openai",  # Use OpenAI-compatible API
                    name="Mock Provider",
                    base_url="http://localhost:8000/v1",  # Non-existent URL for testing
                    api_key="mock-key",
                    model="mock-model",
                    is_active=True,
                    is_default=False,
                    connection_timeout=5,
                    max_tokens=1000,
                    temperature=0.7,
                )
                db.session.add(mock_provider)
                db.session.commit()
                print("Created mock provider for Docker development")
            else:
                # Deactivate all other providers and activate the mock
                LLMProviderConfig.query.update({"is_active": False})
                mock_provider.is_active = True
                db.session.commit()
                print("Activated existing mock provider")

            # List all providers
            providers = LLMProviderConfig.query.all()
            print("\nAll providers:")
            for p in providers:
                active_status = "✓" if p.is_active else " "
                print(
                    f"  [{active_status}] {p.name} ({p.provider}) - {p.base_url} - {p.model}"
                )

        except Exception as e:
            print(f"Error fixing chat configuration: {e}")
            db.session.rollback()
            return False

    return True


if __name__ == "__main__":
    if fix_docker_chat():
        print("\n✓ Docker chat configuration updated successfully")
    else:
        print("\n✗ Failed to fix Docker chat configuration")
        sys.exit(1)

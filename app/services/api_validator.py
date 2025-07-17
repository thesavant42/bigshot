"""
API key validation service
"""

import asyncio
from app.services.external_apis import APIValidator as ExternalAPIValidator


class APIValidator:
    """Service for validating API keys"""

    def __init__(self):
        self.external_validator = ExternalAPIValidator()

    def validate_key(self, service, key):
        """Validate API key format"""
        return self.external_validator.validate_key(service, key)

    def test_key(self, service, key):
        """Test API key functionality"""
        # Since test_key is async, we need to run it in an event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.external_validator.test_key(service, key)
            )
            loop.close()
            return result
        except Exception as e:
            return {"valid": False, "error": str(e)}

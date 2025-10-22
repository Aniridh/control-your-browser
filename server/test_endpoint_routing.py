"""
Test script for Friendliai auto-endpoint routing functionality.
This script tests the automatic detection of dedicated vs serverless endpoints.
"""

import asyncio
import os
import sys
from unittest.mock import patch, MagicMock

# Add the server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.friendliai_client import FriendliaiClient

class MockSettings:
    def __init__(self, friendliai_api_key="test_key", friendliai_endpoint=None, gemini_api_key="test_gemini_key"):
        self.FRIENDLIAI_API_KEY = friendliai_api_key
        self.FRIENDLIAI_ENDPOINT = friendliai_endpoint
        self.GEMINI_API_KEY = gemini_api_key

async def test_serverless_endpoint():
    """Test that serverless endpoint is used when no dedicated endpoint is configured."""
    print("Testing serverless endpoint routing...")
    
    settings = MockSettings(friendliai_endpoint=None)
    client = FriendliaiClient(settings)
    
    print(f"Resolved base URL: {client.friendliai_base_url}")
    assert client.friendliai_base_url == "https://api.friendli.ai", f"Expected serverless URL, got {client.friendliai_base_url}"
    print("✓ Serverless endpoint routing works correctly")

async def test_dedicated_endpoint_success():
    """Test that dedicated endpoint is used when it's reachable."""
    print("\nTesting dedicated endpoint routing (success case)...")
    
    # Mock a successful response from the dedicated endpoint
    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        
        settings = MockSettings(friendliai_endpoint="https://custom.friendli.ai")
        client = FriendliaiClient(settings)
        
        print(f"Resolved base URL: {client.friendliai_base_url}")
        assert client.friendliai_base_url == "https://custom.friendli.ai", f"Expected dedicated URL, got {client.friendliai_base_url}"
        print("✓ Dedicated endpoint routing works correctly")

async def test_dedicated_endpoint_fallback():
    """Test that serverless endpoint is used when dedicated endpoint fails."""
    print("\nTesting dedicated endpoint fallback...")
    
    # Mock a failed response from the dedicated endpoint
    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        
        settings = MockSettings(friendliai_endpoint="https://unreachable.friendli.ai")
        client = FriendliaiClient(settings)
        
        print(f"Resolved base URL: {client.friendliai_base_url}")
        assert client.friendliai_base_url == "https://api.friendli.ai", f"Expected fallback to serverless URL, got {client.friendliai_base_url}"
        print("✓ Dedicated endpoint fallback works correctly")

async def test_dedicated_endpoint_exception_fallback():
    """Test that serverless endpoint is used when dedicated endpoint throws an exception."""
    print("\nTesting dedicated endpoint exception fallback...")
    
    # Mock an exception from the dedicated endpoint
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = Exception("Connection failed")
        
        settings = MockSettings(friendliai_endpoint="https://broken.friendli.ai")
        client = FriendliaiClient(settings)
        
        print(f"Resolved base URL: {client.friendliai_base_url}")
        assert client.friendliai_base_url == "https://api.friendli.ai", f"Expected fallback to serverless URL, got {client.friendliai_base_url}"
        print("✓ Dedicated endpoint exception fallback works correctly")

async def test_empty_endpoint_url():
    """Test that serverless endpoint is used when endpoint URL is empty."""
    print("\nTesting empty endpoint URL...")
    
    settings = MockSettings(friendliai_endpoint="")
    client = FriendliaiClient(settings)
    
    print(f"Resolved base URL: {client.friendliai_base_url}")
    assert client.friendliai_base_url == "https://api.friendli.ai", f"Expected serverless URL, got {client.friendliai_base_url}"
    print("✓ Empty endpoint URL handling works correctly")

async def main():
    """Run all endpoint routing tests."""
    print("Testing Friendliai Auto-Endpoint Routing")
    print("=" * 50)
    
    try:
        await test_serverless_endpoint()
        await test_dedicated_endpoint_success()
        await test_dedicated_endpoint_fallback()
        await test_dedicated_endpoint_exception_fallback()
        await test_empty_endpoint_url()
        
        print("\n" + "=" * 50)
        print("✅ All endpoint routing tests passed!")
        print("\nThe auto-endpoint routing functionality is working correctly:")
        print("- Uses serverless API when no dedicated endpoint is configured")
        print("- Uses dedicated endpoint when it's reachable")
        print("- Falls back to serverless API when dedicated endpoint fails")
        print("- Handles exceptions gracefully")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

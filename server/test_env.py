"""
Environment configuration verification script for ScreenPilot Research Copilot.
Run this script to verify that all required API keys and settings are properly configured.
"""

import os
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import settings

def test_keys():
    """Test and display the status of all configuration keys."""
    print("🔑 ScreenPilot Configuration Status:")
    print("=" * 40)
    print(f"Friendliai API Key: {'✅ Set' if settings.FRIENDLIAI_API_KEY else '❌ Missing'}")
    print(f"Gemini API Key: {'✅ Set' if settings.GEMINI_API_KEY else '❌ Missing'}")
    print(f"Weaviate URL: {settings.WEAVIATE_URL or '❌ Not set'}")
    print(f"Weaviate API Key: {'✅ Set' if settings.WEAVIATE_API_KEY else '❌ Not set (optional)'}")
    print(f"OpenAI API Key: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Missing'}")
    print(f"Port: {settings.PORT}")
    print("=" * 40)
    
    # Check for critical missing keys
    missing_keys = []
    if not settings.FRIENDLIAI_API_KEY:
        missing_keys.append("FRIENDLIAI_API_KEY")
    if not settings.OPENAI_API_KEY:
        missing_keys.append("OPENAI_API_KEY")
    if not settings.WEAVIATE_URL:
        missing_keys.append("WEAVIATE_URL")
    
    if missing_keys:
        print("⚠️  Critical missing configuration:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n💡 Please update your .env file with the missing keys.")
        return False
    else:
        print("✅ All critical configuration is present!")
        return True

def test_connections():
    """Test connections to external services."""
    print("\n🔌 Testing Service Connections:")
    print("=" * 40)
    
    # Test Weaviate connection
    try:
        from utils.weaviate_client import get_client
        client = get_client()
        client.is_ready()
        print("✅ Weaviate connection: OK")
    except Exception as e:
        print(f"❌ Weaviate connection: Failed - {str(e)}")
    
    # Test OpenAI embedding model
    try:
        from utils.llamaindex_client import LlamaIndexClient
        client = LlamaIndexClient()
        embed_model = client.get_embedding_model()
        print("✅ OpenAI embedding model: OK")
    except Exception as e:
        print(f"❌ OpenAI embedding model: Failed - {str(e)}")

if __name__ == "__main__":
    print("🚀 ScreenPilot Research Copilot - Environment Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_keys()
    
    # Test connections if config is OK
    if config_ok:
        test_connections()
    
    print("\n" + "=" * 50)
    print("Test completed!")

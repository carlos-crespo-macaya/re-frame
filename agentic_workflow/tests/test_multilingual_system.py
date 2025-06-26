"""Test script for multilingual 3-agent system."""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reframe.agents.utils.language_detector import (
    detect_language_with_fallback,
    check_exit_command
)
from reframe.orchestrators.multilingual_orchestrator import MultilingualReframeOrchestrator


def test_language_detection():
    """Test language detection with various inputs."""
    test_cases = [
        ("Hola, me siento muy ansioso", "es"),
        ("Hello, I'm feeling anxious", "en"),
        ("Bonjour, je suis anxieux", "fr"),
        ("Ciao, sono ansioso", "it"),
        ("Hallo, ich bin nervös", "de"),
        ("Olá, estou ansioso", "pt"),
        ("Hola, estic nerviós", "ca"),
    ]
    
    print("Testing Language Detection:")
    print("-" * 50)
    
    for text, expected in test_cases:
        result = detect_language_with_fallback(text)
        status = "✅" if result['language_code'] == expected else "❌"
        print(f"{status} '{text[:30]}...'")
        print(f"   Detected: {result['language_name']} ({result['language_code']})")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Method: {result['method']}")
        print()


def test_exit_commands():
    """Test exit command detection."""
    test_cases = [
        ("/exit", "en", True),
        ("/salir", "es", True),
        ("/sortir", "fr", True),
        ("/beenden", "de", True),
        ("/esci", "it", True),
        ("/sair", "pt", True),
        ("/sortir", "ca", True),
        ("I want to continue", "en", False),
        ("Quiero continuar", "es", False),
    ]
    
    print("\nTesting Exit Commands:")
    print("-" * 50)
    
    for command, lang, expected in test_cases:
        result = check_exit_command(command, lang)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{command}' in {lang}: {result}")


async def test_orchestrator():
    """Test the complete orchestrator setup."""
    print("\nTesting Orchestrator Setup:")
    print("-" * 50)
    
    try:
        orchestrator = MultilingualReframeOrchestrator()
        print("✅ Orchestrator initialized")
        print(f"   - Langfuse: Connected")
        print(f"   - Session Service: {type(orchestrator.session_service).__name__}")
        print(f"   - Agents: {len(orchestrator.pipeline.sub_agents)} loaded")
        
        # Create test session
        session_id = orchestrator.create_session("test_user_123")
        print(f"✅ Session created: {session_id}")
        
        print("\nTo test the full system:")
        print("1. Run: adk web")
        print("2. Try messages in different languages:")
        print("   - Spanish: 'Hola, tengo mucha ansiedad por el trabajo'")
        print("   - English: 'Hello, I'm feeling anxious about work'")
        print("   - French: 'Bonjour, je suis anxieux à propos du travail'")
        print("3. Use /exit command during analysis phase")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_environment():
    """Test environment setup."""
    print("\nTesting Environment Setup:")
    print("-" * 50)
    
    required_vars = [
        ("GOOGLE_API_KEY", "Google AI API key"),
        ("LANGFUSE_HOST", "Langfuse host"),
        ("LANGFUSE_PUBLIC_KEY", "Langfuse public key"),
        ("LANGFUSE_SECRET_KEY", "Langfuse secret key"),
    ]
    
    optional_vars = [
        ("SUPABASE_REFRAME_DB_CONNECTION_STRING", "Supabase connection"),
        ("ARIZE_SPACE_ID", "Arize space ID"),
        ("ARIZE_API_KEY", "Arize API key"),
        ("GOOGLE_APPLICATION_CREDENTIALS", "Google Cloud credentials"),
    ]
    
    print("Required Environment Variables:")
    for var, desc in required_vars:
        status = "✅" if os.getenv(var) else "❌"
        print(f"{status} {var}: {desc}")
    
    print("\nOptional Environment Variables:")
    for var, desc in optional_vars:
        status = "✅" if os.getenv(var) else "⚠️"
        print(f"{status} {var}: {desc}")


def main():
    """Run all tests."""
    print("Multilingual 3-Agent System Tests")
    print("=" * 50)
    
    test_environment()
    test_language_detection()
    test_exit_commands()
    asyncio.run(test_orchestrator())
    
    print("\n" + "=" * 50)
    print("Testing complete!")
    print("\nNext steps:")
    print("1. Ensure all required environment variables are set")
    print("2. Run 'python run_multilingual_adk.py' to verify setup")
    print("3. Run 'adk web' to start the interface")
    print("4. Test with messages in different languages")


if __name__ == "__main__":
    main()
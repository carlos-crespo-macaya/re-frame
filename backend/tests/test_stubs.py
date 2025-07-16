"""Test that stubs exist and are properly structured."""

from pathlib import Path


def test_stub_files_exist():
    """Test that stub files exist in the correct location."""
    stubs_path = Path(__file__).parent / "stubs"
    
    # Check google stub exists
    google_stub = stubs_path / "google" / "__init__.py"
    assert google_stub.exists(), f"Google stub not found at {google_stub}"
    
    # Check langdetect stub exists
    langdetect_stub = stubs_path / "langdetect" / "__init__.py"
    assert langdetect_stub.exists(), f"Langdetect stub not found at {langdetect_stub}"


def test_stub_structure():
    """Test that stubs have the expected structure."""
    stubs_path = Path(__file__).parent / "stubs"
    
    # Read and verify google stub content
    google_stub = stubs_path / "google" / "__init__.py"
    content = google_stub.read_text()
    assert "class adk:" in content
    assert "class agents:" in content
    assert "class genai:" in content
    assert "class cloud:" in content
    
    # Read and verify langdetect stub content
    langdetect_stub = stubs_path / "langdetect" / "__init__.py"
    content = langdetect_stub.read_text()
    assert "def detect(" in content
    assert "def detect_langs(" in content
    assert "class LangDetectException" in content
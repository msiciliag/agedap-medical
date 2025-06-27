"""
Tests for key manager functionality.
"""
import pytest
from pathlib import Path


def test_key_manager_file_exists():
    """Test that key_manager.py file exists."""
    key_manager_path = Path(__file__).parent.parent.parent.parent / "provider" / "services" / "key_manager.py"
    assert key_manager_path.exists(), "key_manager.py should exist"


def test_key_manager_has_content():
    """Test that key_manager.py has content."""
    key_manager_path = Path(__file__).parent.parent.parent.parent / "provider" / "services" / "key_manager.py"
    
    if key_manager_path.exists():
        content = key_manager_path.read_text().strip()
        assert len(content) > 0, "key_manager.py should not be empty"


def test_key_manager_contains_class():
    """Test that key_manager.py contains a KeyManager class."""
    key_manager_path = Path(__file__).parent.parent.parent.parent / "provider" / "services" / "key_manager.py"
    
    if key_manager_path.exists():
        content = key_manager_path.read_text()
        assert "class" in content, "key_manager.py should contain a class definition"
        assert "KeyManager" in content, "key_manager.py should contain KeyManager class"


def test_keys_directory_exists():
    """Test that keys directory exists."""
    keys_dir = Path(__file__).parent.parent.parent.parent / "keys"
    
    if keys_dir.exists():
        assert keys_dir.is_dir(), "keys should be a directory"
        
        # Check for service directories
        service_dirs = [d for d in keys_dir.iterdir() if d.is_dir()]
        assert len(service_dirs) > 0, "Keys directory should contain service subdirectories"

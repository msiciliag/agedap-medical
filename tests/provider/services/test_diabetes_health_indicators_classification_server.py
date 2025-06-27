"""
Tests for diabetes health indicators classification server.
"""
import pytest
from pathlib import Path


def test_diabetes_server_file_exists():
    """Test that diabetes server file exists."""
    server_path = Path(__file__).parent.parent.parent.parent / "provider" / "services" / "diabetes_health_indicators_classification_server.py"
    assert server_path.exists(), "diabetes_health_indicators_classification_server.py should exist"


def test_diabetes_server_has_content():
    """Test that diabetes server has content."""
    server_path = Path(__file__).parent.parent.parent.parent / "provider" / "services" / "diabetes_health_indicators_classification_server.py"
    
    if server_path.exists():
        content = server_path.read_text().strip()
        assert len(content) > 0, "diabetes_health_indicators_classification_server.py should not be empty"


def test_diabetes_server_contains_class():
    """Test that diabetes server contains expected content."""
    server_path = Path(__file__).parent.parent.parent.parent / "provider" / "services" / "diabetes_health_indicators_classification_server.py"
    
    if server_path.exists():
        content = server_path.read_text()
        assert "class" in content, "diabetes_health_indicators_classification_server.py should contain a class"

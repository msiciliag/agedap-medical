"""
Tests for base service functionality.
"""
import pytest
from pathlib import Path


def test_base_service_file_exists():
    """Test that base_service.py file exists."""
    service_path = Path(__file__).parent.parent.parent.parent / "provider" / "services" / "base_service.py"
    assert service_path.exists(), "base_service.py should exist"


def test_base_service_has_content():
    """Test that base_service.py has content."""
    service_path = Path(__file__).parent.parent.parent.parent / "provider" / "services" / "base_service.py"
    
    if service_path.exists():
        content = service_path.read_text().strip()
        assert len(content) > 0, "base_service.py should not be empty"


def test_base_service_contains_expected_classes():
    """Test that base_service.py contains expected class definitions."""
    service_path = Path(__file__).parent.parent.parent.parent / "provider" / "services" / "base_service.py"
    
    if service_path.exists():
        content = service_path.read_text()
        
        # Check for expected class or function definitions
        expected_elements = [
            "class",  # Should contain at least one class
            "def",    # Should contain at least one function/method
        ]
        
        for element in expected_elements:
            assert element in content, f"base_service.py should contain {element} definitions"


def test_services_directory_structure():
    """Test that services directory has expected files."""
    services_dir = Path(__file__).parent.parent.parent.parent / "provider" / "services"
    
    expected_files = [
        "base_service.py",
        "key_manager.py",
        "breast_cancer_screening_server.py",
        "diabetes_health_indicators_classification_server.py"
    ]
    
    for expected_file in expected_files:
        file_path = services_dir / expected_file
        assert file_path.exists(), f"Expected service file missing: {expected_file}"

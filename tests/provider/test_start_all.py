"""
Tests for provider start_all functionality.
"""
import pytest
from pathlib import Path


def test_start_all_file_exists():
    """Test that start_all.py file exists."""
    start_all_path = Path(__file__).parent.parent.parent / "provider" / "start_all.py"
    assert start_all_path.exists(), "start_all.py should exist"


def test_start_all_has_content():
    """Test that start_all.py has content."""
    start_all_path = Path(__file__).parent.parent.parent / "provider" / "start_all.py"
    
    if start_all_path.exists():
        content = start_all_path.read_text().strip()
        assert len(content) > 0, "start_all.py should not be empty"


def test_services_directory_exists():
    """Test that services directory exists."""
    services_dir = Path(__file__).parent.parent.parent / "provider" / "services"
    assert services_dir.exists(), "services directory should exist"


def test_service_files_exist():
    """Test that service files exist."""
    services_dir = Path(__file__).parent.parent.parent / "provider" / "services"
    
    expected_services = [
        "base_service.py",
        "breast_cancer_screening_server.py",
        "diabetes_health_indicators_classification_server.py", 
        "key_manager.py"
    ]
    
    for service_file in expected_services:
        service_path = services_dir / service_file
        assert service_path.exists(), f"Service file missing: {service_file}"


def test_service_files_have_content():
    """Test that service files have content."""
    services_dir = Path(__file__).parent.parent.parent / "provider" / "services"
    
    service_files = [
        "base_service.py",
        "key_manager.py"
    ]
    
    for service_file in service_files:
        service_path = services_dir / service_file
        if service_path.exists():
            content = service_path.read_text().strip()
            assert len(content) > 0, f"{service_file} should not be empty"
"""
Tests for patient app configuration.
"""
import pytest
import os
from pathlib import Path


def test_app_config_file_exists():
    """Test that app_config.py file exists."""
    config_path = Path(__file__).parent.parent.parent / "patient_app" / "src" / "app_config.py"
    assert config_path.exists(), "app_config.py should exist"


def test_app_config_contains_expected_content():
    """Test that app_config.py contains expected configuration."""
    config_path = Path(__file__).parent.parent.parent / "patient_app" / "src" / "app_config.py"
    
    if config_path.exists():
        content = config_path.read_text()
        
        # Check for expected configuration variables
        expected_vars = [
            "STORAGE_PREFIX",
            "USER_PATIENT_IDS", 
            "HOSPITAL_LIST",
            "SERVICE_CONFIGS",
            "APP_LEVEL_STORAGE_KEYS"
        ]
        
        for var in expected_vars:
            assert var in content, f"Configuration variable {var} should be defined"
            
        # Check for specific users
        assert "alice" in content, "alice user should be configured"
        assert "maria" in content, "maria user should be configured"
        
        # Check for service configurations
        assert "breast_cancer" in content, "breast cancer service should be configured"
        assert "diabetes" in content, "diabetes service should be configured"


def test_patient_app_structure():
    """Test that patient app has expected directory structure."""
    app_dir = Path(__file__).parent.parent.parent / "patient_app" / "src"
    
    expected_files = [
        "main.py",
        "app_config.py",
        "app_init.py", 
        "navigation.py"
    ]
    
    for expected_file in expected_files:
        file_path = app_dir / expected_file
        assert file_path.exists(), f"Expected file missing: {expected_file}"
        
    expected_dirs = [
        "utils",
        "views",
        "db", 
        "api_client"
    ]
    
    for expected_dir in expected_dirs:
        dir_path = app_dir / expected_dir
        assert dir_path.exists(), f"Expected directory missing: {expected_dir}"
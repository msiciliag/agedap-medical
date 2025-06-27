"""
Tests for patient app initialization.
"""
import pytest
from pathlib import Path


def test_app_init_file_exists():
    """Test that the app_init.py file exists."""
    init_path = Path(__file__).parent.parent.parent / "patient_app" / "src" / "app_init.py"
    assert init_path.exists(), "app_init.py should exist"


def test_app_init_file_has_content():
    """Test that app_init.py has content."""
    init_path = Path(__file__).parent.parent.parent / "patient_app" / "src" / "app_init.py"
    
    if init_path.exists():
        content = init_path.read_text().strip()
        assert len(content) > 0, "app_init.py should not be empty"


def test_required_modules_exist():
    """Test that required modules for app init exist."""
    src_dir = Path(__file__).parent.parent.parent / "patient_app" / "src"
    
    required_modules = [
        'app_config.py',
        'navigation.py'
    ]
    
    for module_name in required_modules:
        module_path = src_dir / module_name
        assert module_path.exists(), f"Required module missing: {module_name}"


def test_views_directory_structure():
    """Test that views directory has expected structure."""
    views_dir = Path(__file__).parent.parent.parent / "patient_app" / "src" / "views"
    
    if views_dir.exists():
        expected_view_files = [
            "__init__.py",
            "config_view.py", 
            "login_view.py",
            "main_app_view.py",
            "service_view.py"
        ]
        
        for view_file in expected_view_files:
            view_path = views_dir / view_file
            assert view_path.exists(), f"Expected view file missing: {view_file}"


def test_utils_directory_structure():
    """Test that utils directory has expected structure."""
    utils_dir = Path(__file__).parent.parent.parent / "patient_app" / "src" / "utils"
    
    if utils_dir.exists():
        expected_util_files = [
            "data_mapper.py",
            "db.py", 
            "fhir.py",
            "omop.py"
        ]
        
        for util_file in expected_util_files:
            util_path = utils_dir / util_file
            assert util_path.exists(), f"Expected util file missing: {util_file}"
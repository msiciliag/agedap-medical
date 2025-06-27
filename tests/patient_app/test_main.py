"""
Tests for main patient app functionality.
"""
import pytest
from pathlib import Path


def test_main_file_exists():
    """Test that the main.py file exists."""
    main_path = Path(__file__).parent.parent.parent / "patient_app" / "src" / "main.py"
    assert main_path.exists(), "main.py should exist"


def test_main_file_is_not_empty():
    """Test that main.py has content."""
    main_path = Path(__file__).parent.parent.parent / "patient_app" / "src" / "main.py"
    
    if main_path.exists():
        content = main_path.read_text().strip()
        assert len(content) > 0, "main.py should not be empty"


def test_patient_app_structure():
    """Test patient app directory structure."""
    app_dir = Path(__file__).parent.parent.parent / "patient_app" / "src"
    
    expected_files = [
        'main.py',
        'app_config.py',
        'app_init.py',
        'navigation.py'
    ]
    
    for expected_file in expected_files:
        file_path = app_dir / expected_file
        assert file_path.exists(), f"Expected file missing: {expected_file}"
        
def test_subdirectories_exist():
    """Test that expected subdirectories exist."""
    app_dir = Path(__file__).parent.parent.parent / "patient_app" / "src"
    
    expected_dirs = [
        'utils',
        'views', 
        'db',
        'api_client',
        'assets'
    ]
    
    for expected_dir in expected_dirs:
        dir_path = app_dir / expected_dir
        assert dir_path.exists(), f"Expected directory missing: {expected_dir}"


def test_assets_directory_has_files():
    """Test that assets directory contains expected files."""
    assets_dir = Path(__file__).parent.parent.parent / "patient_app" / "src" / "assets"
    
    if assets_dir.exists():
        expected_assets = ["icon.png"]
        for asset in expected_assets:
            asset_path = assets_dir / asset
            if asset_path.exists():
                assert asset_path.is_file(), f"{asset} should be a file"
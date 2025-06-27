"""
Tests for the main project structure and configuration.
"""
import pytest
from pathlib import Path


def test_project_root_structure():
    """Test that the project root has expected structure."""
    project_root = Path(__file__).parent.parent
    
    expected_files = [
        "pyproject.toml",
        "README.md", 
        "uv.lock",
        "key_auth_config.ini"
    ]
    
    for expected_file in expected_files:
        file_path = project_root / expected_file
        assert file_path.exists(), f"Expected project file missing: {expected_file}"
        
    expected_dirs = [
        "patient_app",
        "provider",
        "standard_definitions",
        "tests",
        "keys"
    ]
    
    for expected_dir in expected_dirs:
        dir_path = project_root / expected_dir
        assert dir_path.exists(), f"Expected project directory missing: {expected_dir}"


def test_pyproject_toml_content():
    """Test that pyproject.toml has expected content."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        
        # Check for project name
        assert "agedap-medical" in content, "Project name should be in pyproject.toml"
        
        # Check for expected dependencies
        expected_deps = [
            "fhir-resources",
            "flask", 
            "flet",
            "pytest",
            "requests",
            "concrete-ml"
        ]
        
        for dep in expected_deps:
            assert dep in content, f"Expected dependency missing: {dep}"


def test_readme_exists():
    """Test that README.md exists and has content."""
    readme_path = Path(__file__).parent.parent / "README.md"
    
    assert readme_path.exists(), "README.md should exist"
    
    if readme_path.exists():
        content = readme_path.read_text().strip()
        assert len(content) > 0, "README.md should not be empty"


def test_config_files_exist():
    """Test that configuration files exist."""
    project_root = Path(__file__).parent.parent
    
    config_files = [
        "key_auth_config.ini",
        "pytest.ini"
    ]
    
    for config_file in config_files:
        config_path = project_root / config_file
        assert config_path.exists(), f"Configuration file missing: {config_file}"


def test_keys_directory_structure():
    """Test that keys directory has expected structure."""
    keys_dir = Path(__file__).parent.parent / "keys"
    
    if keys_dir.exists():
        # Should have subdirectories for each service
        service_dirs = list(keys_dir.iterdir())
        assert len(service_dirs) > 0, "Keys directory should contain service subdirectories"
        
        for service_dir in service_dirs:
            if service_dir.is_dir():
                # Each service dir should have key files
                key_files = list(service_dir.glob("*.txt"))
                json_files = list(service_dir.glob("*.json"))
                
                assert len(key_files) > 0 or len(json_files) > 0, f"Service directory {service_dir.name} should contain key files"

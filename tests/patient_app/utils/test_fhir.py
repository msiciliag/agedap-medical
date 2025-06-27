"""
Tests for FHIR utility functions.
"""
import pytest
from pathlib import Path


def test_fhir_file_exists():
    """Test that fhir.py file exists."""
    fhir_path = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "utils" / "fhir.py"
    assert fhir_path.exists(), "fhir.py should exist"


def test_fhir_file_has_content():
    """Test that fhir.py has content."""
    fhir_path = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "utils" / "fhir.py"
    
    if fhir_path.exists():
        content = fhir_path.read_text().strip()
        assert len(content) > 0, "fhir.py should not be empty"


def test_fhir_contains_functions():
    """Test that fhir.py contains expected function definitions."""
    fhir_path = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "utils" / "fhir.py"
    
    if fhir_path.exists():
        content = fhir_path.read_text()
        
        # Check for expected functions
        expected_functions = [
            "get_patient_data",
            "_load_bundle_from_file"
        ]
        
        for func in expected_functions:
            assert func in content, f"Function {func} should be defined in fhir.py"


def test_fhir_data_directory_exists():
    """Test that FHIR data directory exists."""
    fhir_data_dir = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "data" / "fhir_bundles"
    
    if fhir_data_dir.exists():
        assert fhir_data_dir.is_dir(), "fhir_bundles should be a directory"
    else:
        pytest.skip("FHIR bundles directory does not exist")


def test_fhir_imports():
    """Test that fhir.py contains expected imports."""
    fhir_path = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "utils" / "fhir.py"
    
    if fhir_path.exists():
        content = fhir_path.read_text()
        
        # Check for FHIR-related imports
        fhir_related = [
            "Patient",
            "Bundle",
            "fhir"
        ]
        
        # At least some FHIR-related content should be present
        has_fhir_content = any(term in content for term in fhir_related)
        assert has_fhir_content, "fhir.py should contain FHIR-related content"

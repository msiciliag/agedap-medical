"""
Tests for FHIR functionality.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the patient_app/src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../patient_app/src'))

try:
    from utils.fhir import get_patient_data, _load_bundle_from_file
    from app_config import USER_PATIENT_IDS
except ImportError as e:
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


def test_user_patient_ids_exist():
    """Test that user patient IDs are available."""
    assert USER_PATIENT_IDS is not None
    assert isinstance(USER_PATIENT_IDS, dict)
    assert len(USER_PATIENT_IDS) > 0


@patch('utils.fhir.requests.get')
def test_get_patient_data_success(mock_get):
    """Test successful patient data retrieval."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "resourceType": "Patient",
        "id": "test-patient",
        "name": [{"family": "Doe", "given": ["John"]}],
        "gender": "male",
        "birthDate": "1990-01-01"
    }
    mock_get.return_value = mock_response
    
    result = get_patient_data("test-patient", "https://hapi.fhir.org/baseR5")
    
    assert result is not None
    assert result.id == "test-patient"


@patch('utils.fhir.requests.get')
def test_get_patient_data_not_found(mock_get):
    """Test patient not found scenario."""
    # Mock 404 response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = mock_response
    
    result = get_patient_data("nonexistent-patient", "https://hapi.fhir.org/baseR5")
    
    assert result is None


def test_load_bundle_from_file_not_exists():
    """Test loading bundle from non-existent file."""
    result = _load_bundle_from_file("/path/that/does/not/exist.json")
    assert result is None


def test_load_bundle_from_file_invalid_json(tmp_path):
    """Test loading bundle from invalid JSON file."""
    invalid_json_file = tmp_path / "invalid.json"
    invalid_json_file.write_text("{ invalid json content")
    
    result = _load_bundle_from_file(str(invalid_json_file))
    assert result is None


def test_load_bundle_from_file_valid_bundle(tmp_path):
    """Test loading valid FHIR bundle."""
    valid_bundle = {
        "resourceType": "Bundle",
        "id": "test-bundle",
        "type": "collection",
        "entry": []
    }
    
    bundle_file = tmp_path / "valid_bundle.json"
    import json
    bundle_file.write_text(json.dumps(valid_bundle))
    
    result = _load_bundle_from_file(str(bundle_file))
    assert result is not None
    assert result.id == "test-bundle"


class TestFHIRBundleLoading:
    """Test class for FHIR bundle loading functionality."""
    
    def test_patient_ids_configuration(self):
        """Test that patient IDs are properly configured."""
        for username, patient_id in USER_PATIENT_IDS.items():
            assert isinstance(username, str)
            assert isinstance(patient_id, str)
            assert len(patient_id) > 0
            assert patient_id.isdigit()  # Assuming patient IDs are numeric

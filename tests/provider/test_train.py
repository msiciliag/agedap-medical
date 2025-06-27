"""
Tests for provider training functionality.
"""
import pytest
from pathlib import Path


def test_train_file_exists():
    """Test that the train.py file exists."""
    train_path = Path(__file__).parent.parent.parent / "provider" / "train.py"
    assert train_path.exists(), "train.py should exist"


def test_training_config_file_exists():
    """Test that the training configuration file exists."""
    config_path = Path(__file__).parent.parent.parent / "provider" / "training_config.yaml"
    assert config_path.exists(), "training_config.yaml should exist"


def test_start_all_script_exists():
    """Test that the start_all script exists."""
    start_all_path = Path(__file__).parent.parent.parent / "provider" / "start_all.py"
    assert start_all_path.exists(), "start_all.py should exist"


def test_provider_directory_structure():
    """Test that provider directory has expected structure."""
    provider_dir = Path(__file__).parent.parent.parent / "provider"
    
    assert provider_dir.exists()
    assert (provider_dir / "services").exists()
    
    # Check for service files
    services_dir = provider_dir / "services"
    expected_files = [
        "base_service.py",
        "breast_cancer_screening_server.py", 
        "diabetes_health_indicators_classification_server.py",
        "key_manager.py"
    ]
    
    for expected_file in expected_files:
        file_path = services_dir / expected_file
        assert file_path.exists(), f"Expected service file missing: {expected_file}"


def test_provider_files_have_content():
    """Test that provider files are not empty."""
    provider_dir = Path(__file__).parent.parent.parent / "provider"
    
    files_to_check = [
        "train.py",
        "start_all.py"
    ]
    
    for file_name in files_to_check:
        file_path = provider_dir / file_name
        if file_path.exists():
            content = file_path.read_text().strip()
            assert len(content) > 0, f"{file_name} should not be empty"


def test_keys_directory_structure():
    """Test that keys directory exists and has expected structure."""
    keys_dir = Path(__file__).parent.parent.parent / "keys"
    
    if keys_dir.exists():
        # Check for service subdirectories
        expected_service_dirs = [
            "Breast Cancer Screening",
            "Diabetes Health Indicators Classification"
        ]
        
        for service_dir in expected_service_dirs:
            service_path = keys_dir / service_dir
            if service_path.exists():
                # Check for expected files in service directory
                expected_files = ["server_xpub.txt", "used.json", "valid.json"]
                for expected_file in expected_files:
                    file_path = service_path / expected_file
                    assert file_path.exists(), f"Expected key file missing: {service_dir}/{expected_file}"
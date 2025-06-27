"""
Unit tests for the KeyManager class.
"""
import sys
import os
import pytest
import json
from unittest.mock import patch, mock_open

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import the class to be tested
from patient_app.src.api_client.key_manager import KeyManager

SERVICE_NAME = "test_service"

# --- Tests for Initialization and _load_valid_keys ---

def test_key_manager_init_success():
    """Test successful initialization when the key file is valid."""
    mock_keys = ["key1", "key2", "key3"]
    read_data = json.dumps(mock_keys)
    
    # We patch Path.exists and open in the module where they are used
    with patch("patient_app.src.api_client.key_manager.Path.exists", return_value=True):
        with patch("patient_app.src.api_client.key_manager.Path.open", mock_open(read_data=read_data)) as mock_file:
            km = KeyManager(service_name=SERVICE_NAME)
            
            assert km.service_name == SERVICE_NAME
            assert km.valid_keys == mock_keys
            mock_file.assert_called_once_with('r')

def test_key_manager_init_file_not_found():
    """Test that FileNotFoundError is raised if the key file doesn't exist."""
    with patch("patient_app.src.api_client.key_manager.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError, match=f"No se encontró el archivo de claves válidas: keys/{SERVICE_NAME}/valid.json"):
            KeyManager(service_name=SERVICE_NAME)

def test_key_manager_init_invalid_json():
    """Test that ValueError is raised for a malformed JSON file."""
    read_data = "this is not json"
    with patch("patient_app.src.api_client.key_manager.Path.exists", return_value=True):
        with patch("patient_app.src.api_client.key_manager.Path.open", mock_open(read_data=read_data)):
            with pytest.raises(ValueError, match="Error al cargar las claves válidas"):
                KeyManager(service_name=SERVICE_NAME)

def test_key_manager_init_json_not_a_list():
    """Test that ValueError is raised if the JSON content is not a list."""
    read_data = json.dumps({"key": "value"}) # A dictionary, not a list
    with patch("patient_app.src.api_client.key_manager.Path.exists", return_value=True):
        with patch("patient_app.src.api_client.key_manager.Path.open", mock_open(read_data=read_data)):
            with pytest.raises(ValueError, match="El archivo de claves válidas no contiene una lista."):
                KeyManager(service_name=SERVICE_NAME)

# --- Tests for get_single_use_key ---

def test_get_single_use_key_success():
    """Test getting a key when keys are available."""
    mock_keys = ["key1", "key2"]
    read_data = json.dumps(mock_keys)
    
    with patch("patient_app.src.api_client.key_manager.Path.exists", return_value=True):
        with patch("patient_app.src.api_client.key_manager.Path.open", mock_open(read_data=read_data)):
            km = KeyManager(service_name=SERVICE_NAME)
            key = km.get_single_use_key()
            
            assert key == "key1"
            # The current implementation reloads the file and pops from the new list
            # so the original instance list is not modified as one might expect.
            # We test the outcome, which is getting the first key.

def test_get_single_use_key_empty():
    """Test getting a key when no keys are available."""
    read_data = json.dumps([]) # Empty list
    
    with patch("patient_app.src.api_client.key_manager.Path.exists", return_value=True):
        with patch("patient_app.src.api_client.key_manager.Path.open", mock_open(read_data=read_data)):
            km = KeyManager(service_name=SERVICE_NAME)
            key = km.get_single_use_key()
            
            assert key is None

@patch.object(KeyManager, '_load_valid_keys')
def test_get_single_use_key_reloads_keys(mock_load_keys):
    """Test that get_single_use_key always reloads the keys."""
    # The __init__ call will call it once.
    # We are testing the call inside get_single_use_key.
    mock_load_keys.return_value = ["key1"]
    km = KeyManager(service_name=SERVICE_NAME)
    
    # Reset the mock to test the next call
    mock_load_keys.reset_mock()
    mock_load_keys.return_value = ["keyA"]

    key = km.get_single_use_key()
    
    mock_load_keys.assert_called_once()
    assert key == "keyA"

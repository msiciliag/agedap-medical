"""
Allows sending encrypted data to the REST API, receive the encrypted response, and decrypt it.
"""

from concrete.ml.deployment import FHEModelClient
import numpy as np
import requests

FHE_DIRECTORY = '/tmp/fhe_client_server_files/'

client = FHEModelClient(path_dir=FHE_DIRECTORY, key_dir="/tmp/keys_client")

def get_prediction(X_new, client=client):
    encrypted_data = client.quantize_encrypt_serialize(X_new)
    serialized_evaluation_keys = client.get_serialized_evaluation_keys()

    files = {
        'encrypted_data': ('encrypted_data.bin', encrypted_data, 'application/octet-stream'),
        'evaluation_keys': ('evaluation_keys.bin', serialized_evaluation_keys, 'application/octet-stream')
    }

    encrypted_response = requests.post(
        "http://127.0.0.1:5001/predict",
        files=files
    )

    return client.deserialize_decrypt_dequantize(encrypted_response.content)

def get_server_info():
    response = requests.get("http://127.0.0.1:5001/info")
    if response.status_code == 200:
        info = response.json()
        required_features = info.get("omop_requirements", {}).get("required_measurements_by_source_value", [])
        expected_format = info.get("omop_requirements", {}).get("expected_input_format", {})
        return {
            "required_features": required_features,
            "expected_format": expected_format
        }
    else:
        response.raise_for_status()

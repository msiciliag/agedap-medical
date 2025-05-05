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
    if encrypted_response.status_code != 200:
        raise ValueError(f"Error in prediction request: {encrypted_response.status_code} - {encrypted_response.text}")
    if encrypted_response.headers.get('Content-Type') != 'text/plain':
        raise ValueError(f"Unexpected response format: {encrypted_response.headers.get('Content-Type')}")
    
    if not encrypted_response.content:
        raise ValueError("Empty response from server.")
    
    return client.deserialize_decrypt_dequantize(encrypted_response.content)

#TODO revisar esta funcion, igual hay partes innecesarias
def get_server_info():
    response = requests.get("http://127.0.0.1:5001/info")
    if response.status_code == 200:
        metadata = response.json()
        if all(key in metadata for key in ["omop_requirements", "fhe_evaluation_keys", 
                                           "prediction_endpoint", "prediction_method"]):
            return metadata
        else:
            raise ValueError("Unexpected response format from server.")
    else:
        response.raise_for_status()

if __name__ == "__main__":

    info = get_server_info()
    required_features = info["omop_requirements"]["required_measurements_by_source_value"]
    n_features = len(required_features)
    
    # TODO In a real scenario, these values should be replaced with actual data that should be extracted from the OMOP database.
    X_new = np.array([[13.54, 14.36, 87.46, 566.3, 0.09779, 0.08129, 0.06664, 0.04781, 0.1885, 0.05766,
                       0.2699, 0.7886, 2.058, 23.56, 0.008462, 0.01460, 0.02387, 0.01315, 0.01980, 0.002300,
                       15.11, 19.26, 99.70, 711.2, 0.14400, 0.17730, 0.23900, 0.12880, 0.2977, 0.07259]])
    
    print(f"Created test data with {n_features} features:")
    for feat, val in zip(required_features, X_new[0]):
        print(f"{feat}: {val:.3f}")

    if X_new.size > 0:
        prediction = get_prediction(X_new)
        print("Decrypted prediction:", prediction)
    else:
        print("No input data available for prediction.")
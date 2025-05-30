from concrete.ml.deployment import FHEModelClient
from .key_manager import KeyManager
import requests

class BaseClient:
    """
    Base client for interacting with a REST API for machine learning predictions.
    This class handles the encryption and decryption of data using ConcreteML (Fully Homomorphic Encryption).
    It is designed to be extended by specific model clients.
    """

    def __init__(self, base_url, fhe_directory, key_directory):
        """
        Initialize the API client with the base URL and FHE model client.

        :param base_url: The base URL of the REST API.
        :param fhe_directory: Directory for FHE client-server files.
        :param key_directory: Directory for FHE keys.
        :param key_manager: Key manager for handling encryption keys.
        """
        self.base_url = base_url
        self.client = FHEModelClient(path_dir=fhe_directory, key_dir=key_directory)
        self.service_name = self._get_service_name()
        self.key_manager = KeyManager(self.service_name)

    def _get_service_name(self):
        """
        Get the service name from the server.

        :return: Service name as a string.
        :raises ValueError: If the response format is unexpected.
        """
        response = requests.get(f"{self.base_url}/get_additional_service_info")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or 'service_name' not in data:
            raise ValueError("Unexpected response format: missing service_name")
        return data['service_name']
    
    def request_info(self):
        """
        Request information from the server about the model and its requirements.

        :return: Model requirements and metadata.
        :raises ValueError: If the response format is unexpected.
        """
        response = requests.get(f"{self.base_url}/get_omop_requirements")
        response.raise_for_status()
        metadata = response.json()
        return metadata
    
    def request_additional_info(self):
        """
        Request additional information from the server about the model and its requirements.

        :return: Model requirements and metadata.
        :raises ValueError: If the response format is unexpected.
        """
        response = requests.get(f"{self.base_url}/get_additional_service_info")
        response.raise_for_status()
        metadata = response.json()
        return metadata
    

    def request_prediction(self, X_new):
        """
        Encrypt data, send it to the server, and decrypt the response.

        :param X_new: Input data as a NumPy array.
        :return: Decrypted and decrypted response from the server.
        """
        encrypted_data = self.client.quantize_encrypt_serialize(X_new)
        serialized_evaluation_keys = self.client.get_serialized_evaluation_keys()
        serialized_single_use_key = self.key_manager.get_single_use_key()

        files = {
            'encrypted_data': ('encrypted_data.bin', encrypted_data, 'application/octet-stream'),
            'evaluation_keys': ('evaluation_keys.bin', serialized_evaluation_keys, 'application/octet-stream'),
            'single_use_key': ('single_use_key.bin', serialized_single_use_key, 'application/octet-stream')
        }

        response = requests.post(f"{self.base_url}/predict", files=files)
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError(f"Unexpected response status code: {response.status_code}")

        return self.client.deserialize_decrypt_dequantize(response.content)
    
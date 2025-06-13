from concrete.ml.deployment import FHEModelClient
from api_client.key_manager import KeyManager
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
        print(f"{self.base_url}/additional_service_info")
        response = requests.get(f"{self.base_url}/additional_service_info")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or 'service_name' not in data:
            raise ValueError("Unexpected response format: missing service_name")
        return data['service_name']

    def _get_label_meanings(self):
        """
        Get the meanings of the labels used in the model.

        :return: Dictionary mapping labels to their meanings.
        """
        response = requests.get(f"{self.base_url}/additional_service_info")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or 'label_meanings' not in data:
            raise ValueError("Unexpected response format: missing label_meanings")
        return data['label_meanings']

    def request_info(self):
        """
        Request the required data structure of the medical data from the server.

        :return: Metadata about the expected input features.
        :raises ValueError: If the response format is unexpected.
        """
        response = requests.get(f"{self.base_url}/omop_requirements")
        response.raise_for_status()
        metadata = response.json()
        return metadata
    
    def request_additional_info(self):
        """
        Request additional information from the server about the model and its requirements.

        :return: Model requirements and metadata.
        :raises ValueError: If the response format is unexpected.
        """
        print(f"Requesting additional service info from {self.base_url}/additional_service_info")
        response = requests.get(f"{self.base_url}/additional_service_info")
        response.raise_for_status()
        metadata = response.json()
        return metadata
    

    def request_prediction(self, X_new):
        """
        Encrypt data, send it to the server, and decrypt the response.

        :param X_new: Input data as a NumPy array.
        :return: Decrypted prediction result as a boolean indicating risk.
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


        response = self.client.deserialize_decrypt_dequantize(response.content)
        label_meanings = self._get_label_meanings()
        print (f"Response: {response}, Label Meanings: {label_meanings}")

        if response[0][0] > response[0][1]:
            prediction_result = 0
        else:
            prediction_result = 1
        prediction_label = label_meanings.get(str(prediction_result))
        print(f"Prediction Result: {prediction_result}, Label: {prediction_label}")
        return prediction_label == "Risk"
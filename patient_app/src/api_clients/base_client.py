from concrete.ml.deployment import FHEModelClient
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
        """
        self.base_url = base_url
        self.client = FHEModelClient(path_dir=fhe_directory, key_dir=key_directory)

    def request_info(self):
        """
        Request information from the server about the model and its requirements.

        :return: Model requirements and metadata.
        :raises ValueError: If the response format is unexpected.
        """
        response = requests.get(f"{self.base_url}/info")
        response.raise_for_status()
        metadata = response.json()
        if "omop_requirements" in metadata:
            return metadata
        raise ValueError("Unexpected response format from server.")
    
    def request_prediction(self, X_new):
        """
        Encrypt data, send it to the server, and decrypt the response.

        :param X_new: Input data as a NumPy array.
        :return: Decrypted and decrypted response from the server.
        """
        encrypted_data = self.client.quantize_encrypt_serialize(X_new)
        serialized_evaluation_keys = self.client.get_serialized_evaluation_keys()

        files = {
            'encrypted_data': ('encrypted_data.bin', encrypted_data, 'application/octet-stream'),
            'evaluation_keys': ('evaluation_keys.bin', serialized_evaluation_keys, 'application/octet-stream')
        }

        response = requests.post(f"{self.base_url}/predict", files=files)
        response.raise_for_status()

        return self.client.deserialize_decrypt_dequantize(response.content)
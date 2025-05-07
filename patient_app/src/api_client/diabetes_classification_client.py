from base_client import BaseClient
import numpy as np

class DiabetesClassificationClient(BaseClient):
    """
    Client for the diabetes classification API. Defines the default URL and directories for FHE files and keys.
    """

    DEFAULT_URL = 'http://127.0.0.1:5002'
    DEFAULT_FHE_DIRECTORY = '/tmp/diabetes_fhe_files/'
    DEFAULT_KEY_DIRECTORY = '/tmp/keys_client'

    def __init__(self, base_url=DEFAULT_URL, fhe_directory=DEFAULT_FHE_DIRECTORY, key_directory=DEFAULT_KEY_DIRECTORY):
        """
        Initialize the DiabetesClassificationClient with real FHE directories.

        :param base_url: The base URL of the REST API.
        :param fhe_directory: Directory for FHE files. Uses default if not provided.
        :param key_directory: Directory for FHE keys. Uses default if not provided.
        """
        super().__init__(base_url, fhe_directory, key_directory)

if __name__ == "__main__":
    # Example usage:
    client = DiabetesClassificationClient()

    # Get server info, including OMOP requirements.
    info = client.request_info()
    required_features = info["omop_requirements"]["required_measurements_by_source_value"]
    n_features = len(required_features)

    # Create test data (in practice, replace with actual measurement values).
    X_new = np.array([[120, 45, 25.3]])  # Example: glucose_level, age, bmi

    print(f"Created test data with {n_features} features:")
    for feat, val in zip(required_features, X_new[0]):
        print(f"{feat}: {val:.3f}")

    if X_new.size > 0:
        prediction = client.request_prediction(X_new)
        print("Decrypted prediction:", prediction)
    else:
        print("No input data available for prediction.")
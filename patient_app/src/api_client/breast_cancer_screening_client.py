from base_client import BaseClient
import numpy as np

class BreastCancerClient(BaseClient):
    """
    Client for the breast cancer prediction API. Defines the default URL and directories for FHE files and keys.
    """

    DEFAULT_URL = 'http://127.0.0.1:5001'
    DEFAULT_FHE_DIRECTORY = '/tmp/breast_cancer_fhe_files/'
    DEFAULT_KEY_DIRECTORY = '/tmp/keys_client'

    def __init__(self, base_url=DEFAULT_URL, fhe_directory=DEFAULT_FHE_DIRECTORY, key_directory=DEFAULT_KEY_DIRECTORY):
        """
        Initialize the BreastCancerClient with real FHE directories.

        :param base_url: The base URL of the REST API.
        :param fhe_directory: Directory for FHE files. Uses default if not provided.
        :param key_directory: Directory for FHE keys. Uses default if not provided.
        :param endpoint: API endpoint for prediction. Uses default if not provided.
        """
        super().__init__(base_url, fhe_directory, key_directory)

if __name__ == "__main__":
    # Example usage:
    client = BreastCancerClient()

    # Get server info, including OMOP requirements.
    info = client.request_info()
    required_features = info["omop_requirements"]["required_measurements_by_source_value"]
    n_features = len(required_features)

    # Create test data (in practice, replace with actual measurement values).
    X_new = np.array([[13.54, 14.36, 87.46, 566.3, 0.09779, 0.08129, 0.06664, 0.04781, 0.1885, 0.05766,
                       0.2699, 0.7886, 2.058, 23.56, 0.008462, 0.01460, 0.02387, 0.01315, 0.01980, 0.002300,
                       15.11, 19.26, 99.70, 711.2, 0.14400, 0.17730, 0.23900, 0.12880, 0.2977, 0.07259]])

    print(f"Created test data with {n_features} features:")
    for feat, val in zip(required_features, X_new[0]):
        print(f"{feat}: {val:.3f}")

    if X_new.size > 0:
        prediction = client.request_prediction(X_new)
        print("Decrypted prediction:", prediction)
    else:
        print("No input data available for prediction.")
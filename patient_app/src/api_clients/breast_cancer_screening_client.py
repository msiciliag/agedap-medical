from api_clients.base_client import BaseClient

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

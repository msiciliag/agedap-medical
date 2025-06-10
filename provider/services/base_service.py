from flask import Flask, request, jsonify
from abc import ABC, abstractmethod
from key_manager import KeyManager
import logging
import yaml
from pathlib import Path


class AIServiceEndpoint(ABC):
    def __init__(self, service_name):
        self.service_name = service_name
        self.fhe_directory = self.load_service_config(service_name)
        self.server = None
        self.key_manager = KeyManager(service_name)
        self.app = self.create_app()
        self.configure_logging()

        try:
            self.server = self.create_server()
        except Exception as e:
            self.app.logger.error(f"Failed to initialize FHEModelServer for {self.service_name}: {e}", exc_info=True)

        self.add_routes()

    def configure_logging(self):
        """Configure logging for the Flask app."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.app.logger.addHandler(handler)
        self.app.logger.setLevel(logging.INFO)
        if not self.app.debug:
            gunicorn_logger = logging.getLogger('gunicorn.error')
            if gunicorn_logger:
                self.app.logger.handlers.extend(gunicorn_logger.handlers)
                self.app.logger.setLevel(gunicorn_logger.level)


    def create_server(self):
        """Initialize and load the FHE model server."""
        from concrete.ml.deployment import FHEModelServer
        self.app.logger.info(f"Loading FHEModelServer from: {self.fhe_directory}")
        server = FHEModelServer(path_dir=self.fhe_directory)
        server.load()
        self.app.logger.info(f"FHEModelServer for {self.service_name} loaded successfully.")
        return server

    def create_app(self):
        """Create a Flask app for this service."""
        app = Flask(self.service_name)
        return app

    @abstractmethod
    def get_omop_requirements(self):
        """
        Subclasses must implement this to define service-specific OMOP requirements,
        including 'required_measurements_by_source_value'.
        :return: A dictionary with required measurements and other metadata.
        e.g.,
        {
            "required_measurements_by_source_value": ["feature1", "feature2"],
            "query_hint": "Some hint",
            "expected_input_format": { ... }
        }
        """
        pass

    @abstractmethod
    def get_fhir_requirements(self):
        """
        Subclasses must implement this to define service-specific FHIR requirements.
        :return: A list of dictionaries describing input variables in FHIR terms.
        e.g.,
        [
            {'name': 'Descriptive Name', 'fhir_resource_type': 'Observation', 
             'fhir_code': {'system': 'uri_del_sistema', 'code': 'codigo_fhir', 'display': 'Optional Display Name'}, 
             'fhir_value_type': 'valueQuantity'}
        ]
        """
        pass

    @abstractmethod
    def get_additional_service_info(self):
        """
        Subclasses must implement this to provide any other service-specific metadata.
        :return: A dictionary with additional service information.
        e.g.,
        {
            "service_name": service_name,
            "description": (
                "This service performs breast cancer screening using machine learning. "
            ),
            "label_meanings": {
                    "0": "No Risk",
                    "1": "Risk"
                }
        }
        """
        pass

    def predict(self):
        """Handles predictions. This logic is common to all FHE services.
        It expects the request to contain the encrypted data, evaluation keys, and a single-use key.
        Returns:
            Response: JSON response with prediction results or error message.
        """
        if not self.server:
            self.app.logger.error("Prediction attempt failed: FHE Model Server not available.")
            return jsonify({"error": "FHE Model Server not loaded or failed to initialize."}), 503
        
        try:
            encrypted_data_file = request.files.get('encrypted_data')
            evaluation_keys_file = request.files.get('evaluation_keys')
            single_use_key_file = request.files.get('single_use_key')
            
            if not encrypted_data_file or not evaluation_keys_file or not single_use_key_file:
                self.app.logger.warning("Prediction failed: Missing files in the request.")
                return jsonify({"error": "Missing files in the request (expected 'encrypted_data', 'evaluation_keys', and 'single_use_key')"}) , 400

            encrypted_data = encrypted_data_file.read()
            serialized_evaluation_keys = evaluation_keys_file.read()
            single_use_key = single_use_key_file.read().decode('utf-8').strip()

            if not self.key_manager.validate_key(single_use_key):
                self.app.logger.warning("Prediction failed: Invalid single-use key.")
                return jsonify({"error": "Invalid single-use key."}), 403
            
            self.app.logger.info(f"Running FHE prediction for {self.service_name}...")
            encrypted_result = self.server.run(encrypted_data, serialized_evaluation_keys)
            self.app.logger.info(f"FHE prediction for {self.service_name} successful.")

            self.key_manager.mark_key_as_used(single_use_key)

            return encrypted_result, 200, {'Content-Type': 'application/octet-stream'}
        except Exception as e:
            self.app.logger.error(f"Prediction error for {self.service_name}: {e}", exc_info=True)
            return jsonify({"error": f"An internal server error occurred during prediction: {str(e)}"}), 500
    
    def get_additional_service_info_endpoint(self):
        return self.get_additional_service_info()

    def add_routes(self):
        """Add all relevant routes for the service."""
        self.app.add_url_rule(f"{base_path}/omop_requirements", f"{self.url_safe_name}_omop", self.get_omop_requirements, methods=['GET'])
        self.app.add_url_rule(f"{base_path}/fhir_requirements", f"{self.url_safe_name}_fhir", self.get_fhir_requirements, methods=['GET'])
        self.app.add_url_rule(f"/{self.service_name}/additional_service_info", "get_additional_service_info_endpoint", self.get_additional_service_info_endpoint, methods=["GET"])
        self.app.add_url_rule(f"/{self.service_name}/predict", "predict", self.predict, methods=["POST"])

    def run(self, port, host='0.0.0.0', debug=False):
        """Run the Flask app for this service."""
        self.app.logger.info(f"Starting {self.model_display_name} service on http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

    def load_service_config(self, service_name):
        """Load service configuration from YAML file.
        
        Args:
            service_name (str): Name of the service to load config for
            
        Returns:
            str: FHE directory path from config
            
        Raises:
            ValueError: If no configuration found for service
        """
        config_path = str(Path(__file__).parent.parent / 'training_config.yaml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            dataset_config = next(
                (d for d in config['datasets'] if d['service_name'] == service_name),
                None
            )
            if not dataset_config:
                raise ValueError(f"No configuration found for service {service_name}")
            return dataset_config['output_directory']


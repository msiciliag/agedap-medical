# --- START OF FILE base_service.py ---

from flask import Flask, request, jsonify
from abc import ABC, abstractmethod
import logging

class AIServiceEndpoint(ABC):
    def __init__(self, service_name, model_display_name, fhe_directory):
        self.service_name = service_name
        self.model_display_name = model_display_name
        self.fhe_directory = fhe_directory
        self.server = None
        self.app = self.create_app()
        self.configure_logging()

        try:
            self.server = self.create_server()
        except Exception as e:
            self.app.logger.error(f"Failed to initialize FHEModelServer for {self.service_name}: {e}", exc_info=True)

        self.add_routes()

    def configure_logging(self):
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
    def get_additional_service_info(self):
        """
        Subclasses must implement this to provide any other service-specific metadata.
        :return: A dictionary with additional service information.
        e.g.,
        {
            "additional_info": "Some additional information about the service",
            "version": "1.0.0"
        }
        """
        pass

    def get_info(self):
        """Provides metadata about the service, including input requirements defined by subclasses."""
        if not self.server:
            return jsonify({
                "error": "FHE Model Server not loaded or failed to initialize.",
                "service_name": self.service_name,
                "model_display_name": self.model_display_name,
            }), 503

        omop_reqs = self.get_omop_requirements()
        additional_info = self.get_additional_service_info()

        if not isinstance(omop_reqs, dict):
            self.app.logger.error(f"get_omop_requirements for {self.service_name} did not return a dictionary.")
            omop_reqs = {"error": "OMOP requirements not configured properly."}

        if not isinstance(additional_info, dict):
            self.app.logger.error(f"get_additional_service_info for {self.service_name} did not return a dictionary.")
            additional_info = {"error": "Additional info not configured properly."}

        metadata = {
            "service_name": self.service_name,
            "model_display_name": self.model_display_name,
            "fhe_directory": self.fhe_directory,
            "omop_requirements": omop_reqs,
            "additional_service_info": additional_info
        }
        return jsonify(metadata)

    def predict(self):
        """Handles predictions. This logic is common to all FHE services."""
        if not self.server:
            self.app.logger.error("Prediction attempt failed: FHE Model Server not available.")
            return jsonify({"error": "FHE Model Server not loaded or failed to initialize."}), 503

        try:
            encrypted_data_file = request.files.get('encrypted_data')
            evaluation_keys_file = request.files.get('evaluation_keys')

            if not encrypted_data_file or not evaluation_keys_file:
                self.app.logger.warning("Prediction failed: Missing files in the request.")
                return "Missing files in the request (expected 'encrypted_data' and 'evaluation_keys')", 400

            encrypted_data = encrypted_data_file.read()
            serialized_evaluation_keys = evaluation_keys_file.read()

            self.app.logger.info(f"Running FHE prediction for {self.service_name}...")
            encrypted_result = self.server.run(encrypted_data, serialized_evaluation_keys)
            self.app.logger.info(f"FHE prediction for {self.service_name} successful.")

            return encrypted_result, 200, {'Content-Type': 'application/octet-stream'}
        except Exception as e:
            self.app.logger.error(f"Prediction error for {self.service_name}: {e}", exc_info=True)
            return jsonify({"error": f"An internal server error occurred during prediction: {str(e)}"}), 500

    def add_routes(self):
        """Add the routes to the Flask app."""
        self.app.add_url_rule('/info', view_func=self.get_info, methods=['GET'])
        self.app.add_url_rule('/get_additional_service_info', view_func=self.get_additional_service_info, methods=['GET'])
        self.app.add_url_rule('/predict', view_func=self.predict, methods=['POST'])

    def run(self, port, host='0.0.0.0', debug=False):
        """Run the Flask app for this service."""
        self.app.logger.info(f"Starting {self.model_display_name} service on http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


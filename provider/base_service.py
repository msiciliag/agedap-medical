from flask import Flask
from abc import ABC, abstractmethod

class AIServiceEndpoint(ABC):
    def __init__(self, service_name, fhe_directory):
        self.service_name = service_name
        self.fhe_directory = fhe_directory
        self.server = self.create_server()
        self.app = self.create_app()
        self.add_routes()

    def create_server(self):
        """Initialize and load the FHE model server."""
        from concrete.ml.deployment import FHEModelServer
        server = FHEModelServer(path_dir=self.fhe_directory)
        server.load()
        return server

    def create_app(self):
        """Create a Flask app for this service."""
        app = Flask(__name__)
        return app

    @abstractmethod
    def get_info(self):
        """Define the service-specific metadata."""
        pass

    @abstractmethod
    def predict(self):
        """Define how to handle predictions."""
        pass

    def add_routes(self):
        """Add the routes to the Flask app."""
        self.app.add_url_rule(f'/info', view_func=self.get_info, methods=['GET'])
        self.app.add_url_rule(f'/predict', view_func=self.predict, methods=['POST'])

    def run(self):
        """Run the Flask app for this service."""
        self.app.run(host='0.0.0.0', port=5001, debug=False)

from base_service import AIServiceEndpoint
from flask import request, jsonify


class BreastCancerScreening(AIServiceEndpoint):
    def __init__(self):
        fhe_directory = '/tmp/breast_cancer_fhe_files/'
        super().__init__('breast_cancer', fhe_directory)

    def get_info(self):
        """Provides metadata about the expected input features."""
        metadata = {
            "omop_requirements": {
                "required_measurements_by_source_value": [
                    "radius1",
                    "texture1",
                    "perimeter1",
                    "area1",
                    "smoothness1",
                    "compactness1",
                    "concavity1",
                    "concave_points1",
                    "symmetry1",
                    "fractal_dimension1",
                    "radius2",
                    "texture2",
                    "perimeter2",
                    "area2",
                    "smoothness2",
                    "compactness2",
                    "concavity2",
                    "concave_points2",
                    "symmetry2",
                    "fractal_dimension2",
                    "radius3",
                    "texture3",
                    "perimeter3",
                    "area3",
                    "smoothness3",
                    "compactness3",
                    "concavity3",
                    "concave_points3",
                    "symmetry3",
                    "fractal_dimension3"
                ]
            }
        }
        return jsonify(metadata)

    def predict(self):
        """Receives encrypted data and evaluation keys, returns encrypted prediction."""
        try:
            encrypted_data_file = request.files.get('encrypted_data')
            evaluation_keys_file = request.files.get('evaluation_keys')

            if not encrypted_data_file or not evaluation_keys_file:
                return "Missing files in the request", 400

            encrypted_data = encrypted_data_file.read()
            serialized_evaluation_keys = evaluation_keys_file.read()

            encrypted_result = self.server.run(encrypted_data, serialized_evaluation_keys)

            return encrypted_result, 200, {'Content-Type': 'text/plain'}

        except Exception as e:
            self.app.logger.error(f"Prediction error: {e}", exc_info=True)
            return jsonify({"error": f"An internal server error occurred: {e}"}), 500

if __name__ == "__main__":
    app = BreastCancerScreening().app
    app.run(host='0.0.0.0', port=5001, debug=False)

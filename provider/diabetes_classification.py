from base_service import AIServiceEndpoint
from flask import request, jsonify

class DiabetesClassification(AIServiceEndpoint):
    def __init__(self):
        fhe_directory = '/tmp/diabetes_fhe_files/'
        super().__init__('diabetes', fhe_directory)

    def get_info(self):
        metadata = {
            "omop_requirements": {
                "required_measurements_by_source_value": [
                    "glucose_level", "age", "bmi", # etc.
                ],
                "query_hint": "Retrieve measurements where measurement_concept_id = 1 and measurement_source_value is in the list above.",
                "expected_input_format": {
                    "structure": "object_with_key_value_pairs",
                    "key": "measurement_source_value",
                    "value": "value_as_number"
                }
            }
        }
        return jsonify(metadata)

    def predict(self):
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

from base_service import AIServiceEndpoint
from flask import jsonify

service_name = "Diabetes Health Indicators Classification"
model_display_name = "diabetes_classification"
fhe_directory = '/tmp/diabetes_fhe_files/' 

class DiabetesClassification(AIServiceEndpoint):

    def __init__(self):
        super().__init__(service_name, model_display_name, fhe_directory)

    def get_omop_requirements(self):
        """Provides metadata about the expected input features."""
        metadata = {
            "omop_requirements": {
                "required_measurements_by_source_value": [
                    "glucose_level", "age", "bmi"  # TODO complete
                ]
            }
        }
        return jsonify(metadata)

    def get_additional_service_info(self):
        """Provides additional data about the service."""
        additional_info = {
            "service_name": service_name,
            "description": (
                "This service performs diabetes classification using machine learning. "
            )
        }
        return jsonify(additional_info)
    
if __name__ == "__main__":
    app = DiabetesClassification().app
    app.run(host='0.0.0.0', port=5002, debug=False)
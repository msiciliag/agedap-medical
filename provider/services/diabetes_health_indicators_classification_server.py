from base_service import AIServiceEndpoint
from flask import jsonify

service_name = "Diabetes Health Indicators Classification"

class DiabetesClassification(AIServiceEndpoint):

    def __init__(self):
        super().__init__(service_name)

    def get_omop_requirements(self):
        """Provides metadata about the expected input features."""
        metadata = [
            "HighBP", "HighChol", "CholCheck", "BMI", "Smoker", "Stroke", 
            "HeartDiseaseorAttack", "PhysActivity", "Fruits", "Veggies", 
            "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost", "GenHlth", 
            "MentHlth", "PhysHlth", "DiffWalk", "Sex", "Age", "Education", "Income"
        ] # TODO define adecuately according to omop
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
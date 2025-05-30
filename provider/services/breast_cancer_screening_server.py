from base_service import AIServiceEndpoint
from flask import jsonify

service_name = "Breast Cancer Screening"

class BreastCancerScreening(AIServiceEndpoint):

    def __init__(self):
        super().__init__(service_name)

    def get_omop_requirements(self):
        """Provides metadata about the expected input features."""
        metadata = [
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
        return jsonify(metadata)

    def get_additional_service_info(self):
        """Provides additional data about the service."""
        additional_info = {
            "service_name": service_name,
            "description": (
                "This service performs breast cancer screening using machine learning. "
            ),
            "label_meanings": {
                "0": "No Risk",
                "1": "Risk"
            }
        }
        return jsonify(additional_info)

if __name__ == "__main__":
    app = BreastCancerScreening().app
    app.run(host='0.0.0.0', port=5001, debug=False)

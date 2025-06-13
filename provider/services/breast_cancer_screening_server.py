import sys
sys.path.append("../..")
from flask import jsonify
from provider.services.base_service import AIServiceEndpoint
from standard_definitions.terminology_definitions import (
    BREAST_CANCER_CONCEPT_START_ID,
    BREAST_CANCER_CODE_SYSTEM,
    BREAST_CANCER_DEFINITIONS
)

SERVICE_NAME = "Breast Cancer Screening"

class BreastCancerScreening(AIServiceEndpoint):
    def __init__(self):
        super().__init__(SERVICE_NAME)
        self._omop_metadata = self._generate_omop_requirements()
        self._fhir_metadata = self._generate_fhir_requirements()

    def _generate_omop_requirements(self):
        """
        Generates the OMOP metadata for breast cancer screening measurements.
        """
        correct_measurements = []
        for category, definitions in BREAST_CANCER_DEFINITIONS.items():
            if category == "Measurement":
                for i, m_def in enumerate(definitions):
                        correct_measurements.append({
                            "measurement_concept_id": BREAST_CANCER_CONCEPT_START_ID + i,
                            "measurement_source_value": m_def["source_value"],
                            "value_name": m_def["value_name"]
                        })  
        return {"measurement": correct_measurements}

    def _generate_fhir_requirements(self):
        """
        Generates the FHIR metadata for breast cancer screening measurements.
        """
        fhir_requirements_list = []
        for measurement in self._omop_metadata.get("measurement", []):
            fhir_requirements_list.append({
                "name": measurement["value_name"],
                "fhir_resource_type": "Observation",
                "fhir_code": {
                    "system": BREAST_CANCER_CODE_SYSTEM,
                    "code": measurement["measurement_source_value"],
                    "display": measurement["measurement_source_value"].replace('_', ' ').title()
                },
                "fhir_value_type": "valueQuantity"
            })
        return fhir_requirements_list
    
    def get_omop_requirements(self):
        return jsonify(self._omop_metadata)

    def get_fhir_requirements(self):
        return jsonify(self._fhir_metadata)

    def get_additional_service_info(self):
        """Provides additional data about the service."""
        additional_info = {
            "service_name": SERVICE_NAME,
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
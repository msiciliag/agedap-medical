from flask import Flask, jsonify
from provider.services.base_service import AIServiceEndpoint
from standard_definitions.terminology_definitions import (
    MEASUREMENT_DEFINITIONS,
    OMOP_CUSTOM_CONCEPT_START_ID,
    FHIR_CUSTOM_CODE_SYSTEM_URI
)

SERVICE_NAME = "Breast Cancer Screening"

OMOP_CUSTOM_CONCEPT_START_ID = 2_000_000_001
FHIR_CUSTOM_CODE_SYSTEM_URI = "http://agedap_medical.com/codes/breast-cancer-screening"

class BreastCancerScreening(AIServiceEndpoint):
    """
    Breast Cancer Screening Service
    This service provides endpoints for breast cancer screening using machine learning.
    """
    def __init__(self, app):
        super().__init__(SERVICE_NAME)
        self._omop_metadata = self._generate_omop_requirements()
        self._fhir_metadata = self._generate_fhir_requirements()

    def _generate_omop_requirements(self):
        """
        Generates the OMOP metadata for breast cancer screening measurements.
        """
        correct_measurements = []
        for i, m_def in enumerate(MEASUREMENT_DEFINITIONS):
            correct_measurements.append({
                "measurement_concept_id": OMOP_CUSTOM_CONCEPT_START_ID + i,
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
                    "system": FHIR_CUSTOM_CODE_SYSTEM_URI,
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
        return jsonify({
            "service_name": self.service_name,
            "description": "This service performs breast cancer screening using machine learning.",
            "label_meanings": {"0": "No Risk", "1": "Risk"}
        })

if __name__ == "__main__":
    app = BreastCancerScreening().app
    app.run(host='0.0.0.0', port=5001, debug=True)
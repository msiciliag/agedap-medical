import sys
sys.path.append("../..") 
from flask import jsonify
from provider.services.base_service import AIServiceEndpoint
from standard_definitions.terminology_definitions import (
    DIABETES_DEFINITIONS,
    DIABETES_CONCEPT_START_ID,
    DIABETES_CODE_SYSTEM
)

SERVICE_NAME = "Diabetes Health Indicators Classification"

class DiabetesClassification(AIServiceEndpoint):

    def __init__(self):
        super().__init__(SERVICE_NAME)
        self.omop_metadata = self._generate_omop_requirements()
        self.fhir_metadata = self._generate_fhir_requirements()

    def _generate_omop_requirements(self):
        omop_reqs = {}
        current_id = DIABETES_CONCEPT_START_ID

        for domain, definitions in DIABETES_DEFINITIONS.items():
            domain_reqs = []
            for m_def in definitions:
                domain_reqs.append({
                    f"{domain.lower()}_concept_id": current_id,
                    f"{domain.lower()}_source_value": m_def["source_value"],
                    "value_name": m_def["value_name"]
                })
                current_id += 1
            omop_reqs[domain.lower()] = domain_reqs
        return omop_reqs

    def _generate_fhir_requirements(self):
        fhir_reqs = []
        for domain, definitions in self.omop_metadata.items():
            for req in definitions:
                fhir_reqs.append({
                    "name": req["value_name"],
                    "fhir_resource_type": domain.title(),
                    "fhir_code": {
                        "system": DIABETES_CODE_SYSTEM,
                        "code": req[f"{domain}_source_value"],
                        "display": req[f"{domain}_source_value"].replace('_', ' ').title()
                    },
                    "fhir_value_type": "valueQuantity" if domain == 'measurement' else 'valueCodeableConcept'
                })
        return fhir_reqs

    def get_omop_requirements(self):
        return jsonify(self.omop_metadata)

    def get_fhir_requirements(self):
        return jsonify(self.fhir_metadata)

    def get_additional_service_info(self):
        """Provides additional data about the service."""
        additional_info = {
            "service_name": SERVICE_NAME,
            "description": (
                "This service performs diabetes classification using machine learning. "
            ),
            "label_meanings": {
                "0": "No Risk",
                "1": "Risk"
            }
        }
        return jsonify(additional_info)
    
if __name__ == "__main__":
    app = DiabetesClassification().app
    app.run(host='0.0.0.0', port=5002, debug=False)
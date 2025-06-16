import sys
sys.path.append("../..")
from flask import jsonify
from provider.services.base_service import AIServiceEndpoint
# Importamos el diccionario maestro y el ID de concepto OMOP base
from standard_definitions.terminology_definitions import ALL_DEFINITIONS

SERVICE_NAME = "Breast Cancer Screening"

class BreastCancerScreening(AIServiceEndpoint):
    
    # ESTA ES LA "LISTA DE LA COMPRA"
    # Define el subconjunto y el orden de los términos que este servicio necesita.
    REQUIRED_DEFINITIONS = [
        "radius1", "texture1", "perimeter1", "area1", "smoothness1", 
        "compactness1", "concavity1", "concave_points1", "symmetry1", 
        "fractal_dimension1", "radius2", "texture2", "perimeter2", "area2", 
        "smoothness2", "compactness2", "concavity2", "concave_points2", 
        "symmetry2", "fractal_dimension2", "radius3", "texture3", "perimeter3", 
        "area3", "smoothness3", "compactness3", "concavity3", 
        "concave_points3", "symmetry3", "fractal_dimension3"
    ]

    def __init__(self):
        super().__init__(SERVICE_NAME)
        self._omop_metadata = self._generate_omop_requirements()
        self._fhir_metadata = self._generate_fhir_requirements()

    def _generate_omop_requirements(self):
        """
        Genera los metadatos OMOP buscando las definiciones requeridas
        en el diccionario maestro y usando sus IDs hardcodeados.
        """
        measurements = []
        for value_name in self.REQUIRED_DEFINITIONS:
            definition = ALL_DEFINITIONS.get(value_name)
            if not definition or definition["domain"] != "Measurement":
                self.app.logger.error(f"Definition for '{value_name}' not found or not a Measurement in ALL_DEFINITIONS.")
                continue 

            omop_concept_id = definition.get("omop_concept_id")
            if omop_concept_id is None:
                self.app.logger.error(f"OMOP Concept ID not defined for '{value_name}' in ALL_DEFINITIONS.")
                continue

            measurements.append({
                "measurement_concept_id": omop_concept_id,
                "measurement_source_value": definition["source_value"],
                "value_name": value_name
            })
        return {"measurement": measurements}

    def _generate_fhir_requirements(self):
        """Genera los requisitos FHIR buscando en el diccionario maestro."""
        fhir_reqs = []
        for value_name in self.REQUIRED_DEFINITIONS:
            definition = ALL_DEFINITIONS.get(value_name)
            if not definition:
                self.app.logger.error(f"Definition for '{value_name}' not found in ALL_DEFINITIONS for FHIR requirements.")
                continue

            fhir_reqs.append({
                "name": value_name,
                "fhir_resource_type": definition["domain"],
                "fhir_code": {
                    "system": definition["fhir_system"],
                    "code": definition["source_value"],
                    "display": definition["source_value"].replace('_', ' ').title()
                },
                # Para el cáncer de mama, todos son valueQuantity.
                # Otros servicios podrían necesitar lógica para determinar esto desde ALL_DEFINITIONS si varía.
                "fhir_value_type": "valueQuantity" 
            })
        return fhir_reqs
    
    def get_omop_requirements(self):
        return self._generate_omop_requirements()

    def get_fhir_requirements(self):
        return self._generate_fhir_requirements()

    def get_additional_service_info(self):
        """Provides additional data about the service."""
        additional_info = {
            "service_name": SERVICE_NAME,
            "description": (
                "This service performs breast cancer screening using machine learning. "
            ),
            "label_meanings": {
                "0": "No Risk", # Benign
                "1": "Risk"     # Malignant
            }
        }
        return jsonify(additional_info)

if __name__ == "__main__":
    service_instance = BreastCancerScreening()
    service_instance.app.run(host='0.0.0.0', port=5001, debug=False)
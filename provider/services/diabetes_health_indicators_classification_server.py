import sys
sys.path.append("../..")
from flask import jsonify
from provider.services.base_service import AIServiceEndpoint
from standard_definitions.terminology_definitions import ALL_DEFINITIONS

SERVICE_NAME = "Diabetes Health Indicators Classification"

class DiabetesClassification(AIServiceEndpoint):
    REQUIRED_DEFINITIONS = [
        # observations   
        "chol_check_last_5_years", "smoker_status", "phys_activity_last_30_days",
        "eats_fruit_daily", "eats_vegetables_daily", "heavy_alcohol_consumer",
        "has_healthcare_coverage", "deferred_doctor_visit_due_to_cost",
        "general_health_scale_1_5", "days_of_poor_mental_health",
        "days_of_poor_physical_health", "has_difficulty_walking", "patient_sex",
        "patient_age", "education_level_scale_1_6", "income_level_scale_1_8",
        # conditions
        "high_blood_pressure_status", "high_cholesterol_status",
        "stroke_history", "heart_disease_or_attack_history",
        # measurements
        "body_mass_index"
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
        omop_reqs = {
            "observation": [],
            "condition": [],
            "measurement": []
        }
        
        for value_name in self.REQUIRED_DEFINITIONS:
            definition = ALL_DEFINITIONS.get(value_name)
            if not definition:
                self.app.logger.error(f"Definition for '{value_name}' not found in ALL_DEFINITIONS for OMOP requirements.")
                continue

            domain_key = definition["domain"].lower()
            if domain_key not in omop_reqs:
                self.app.logger.error(f"Domain '{domain_key}' for value_name '{value_name}' is not a recognized OMOP domain key (observation, condition, measurement).")
                continue

            omop_concept_id = definition.get("omop_concept_id")
            if omop_concept_id is None:
                self.app.logger.error(f"OMOP Concept ID not defined for '{value_name}' in ALL_DEFINITIONS.")
                continue
            
            omop_item = {
                f"{domain_key}_concept_id": omop_concept_id,
                f"{domain_key}_source_value": definition["source_value"],
                "value_name": value_name,
                "is_person_demographic": definition.get("is_person_demographic", False)
            }
            omop_reqs[domain_key].append(omop_item)
            
        return omop_reqs

    def _generate_fhir_requirements(self):
        """Genera los requisitos FHIR buscando en el diccionario maestro."""
        fhir_reqs = []
        for value_name in self.REQUIRED_DEFINITIONS:
            definition = ALL_DEFINITIONS.get(value_name)
            if not definition:
                self.app.logger.error(f"Definition for '{value_name}' not found in ALL_DEFINITIONS for FHIR requirements.")
                continue

            domain = definition["domain"]
            fhir_value_type = "valueQuantity" if domain == "Measurement" else "valueCodeableConcept"

            fhir_reqs.append({
                "name": value_name,
                "fhir_resource_type": domain,
                "fhir_code": {
                    "system": definition["fhir_system"],
                    "code": definition["source_value"],
                    "display": definition["source_value"].replace('_', ' ').title()
                },
                "fhir_value_type": fhir_value_type
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
                "This service uses machine learning to classify diabetes risk based on health indicators. "
                "It requires information about patient observations, conditions, and measurements."
            ),
            "label_meanings": {
                "0": "No Diabetes / No Pre-diabetes", # Corresponds to original dataset's 0
                "1": "Pre-diabetes",                 # Corresponds to original dataset's 1
                "2": "Diabetes"                      # Corresponds to original dataset's 2
                # Note: The FHE model output might be binary (Risk/No Risk).
                # This section should reflect what the /predict endpoint's FHE model actually outputs and how it's interpreted.
                # For now, assuming a binary "Risk" (1) vs "No Risk" (0) similar to breast cancer for simplicity of example.
                # If the model is multi-class, the client-side interpretation of FHE output needs to match.
                # The original UCI dataset for Diabetes (012) has 3 classes.
                # Let's assume the FHE model was trained for binary: 0 (No Diabetes/Pre-diabetes) vs 1 (Diabetes)
                # Or more simply, 0 = No Risk, 1 = Risk (of diabetes or pre-diabetes)
            },
            # Simplified label meanings for a binary risk model:
             "simplified_label_meanings": {
                "0": "Lower Risk of Diabetes",
                "1": "Higher Risk of Diabetes"
            }
            # The actual label_meanings should align with the FHE model's output interpretation.
            # The base_client currently assumes a binary output and "Risk" vs "No Risk"
        }
        # For the purpose of this refactoring, we'll keep the label_meanings simple,
        # assuming the FHE model output is handled by the client as binary risk.
        # The `base_client.py` `request_prediction` method currently interprets the FHE output
        # as binary and looks for a "Risk" label.
        # So, the `label_meanings` here should provide that.
        additional_info["label_meanings"] = {
             "0": "No Risk", # Placeholder, adjust if model output is different
             "1": "Risk"     # Placeholder, adjust if model output is different
        }
        return jsonify(additional_info)
    
if __name__ == "__main__":
    service_instance = DiabetesClassification()
    # The port should be different from other services, e.g., 5002
    service_instance.app.run(host='0.0.0.0', port=5002, debug=False)
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

    def get_omop_requirements(self):
        return self._generate_omop_requirements()
    
    def get_additional_service_info(self):
        """Provides additional data about the service."""
        additional_info = {
            "service_name": SERVICE_NAME,
            "description": (
                "This service uses machine learning to classify diabetes risk based on health indicators. "
            ),
            "label_meanings": {
                "0": "No Risk",
                "1": "Risk"
            }
        }
        return jsonify(additional_info)
    
if __name__ == "__main__":
    service_instance = DiabetesClassification()
    service_instance.app.run(host='0.0.0.0', port=5002, debug=False)
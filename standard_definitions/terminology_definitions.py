# =============================================================================
# This file contains standard definitions for terminology used in the project.
# SINGLE SOURCE OF TRUTH for terminology definitions
# It is necessary because most of the services use very specific terminology
# not defined in most of the standard vocabularies.
# This file represents the "shared knowledge" or "data dictionary"
# agreed upon by data stewards and development teams.
# =============================================================================


OMOP_CUSTOM_CONCEPT_START_ID = 2_000_000_001
FHIR_CUSTOM_CODE_SYSTEM_URI_BASE = "http://agedap_medical.com/codes/"

BREAST_CANCER_CONCEPT_START_ID = 2_000_000_001
BREAST_CANCER_CODE_SYSTEM = f"{FHIR_CUSTOM_CODE_SYSTEM_URI_BASE}breast-cancer-screening"
BREAST_CANCER_DEFINITIONS = {
    "Measurement": [
        {"source_value": "radius_mean", "value_name": "radius1"}, 
        {"source_value": "texture_mean", "value_name": "texture1"},
        {"source_value": "perimeter_mean", "value_name": "perimeter1"},
        {"source_value": "area_mean", "value_name": "area1"},
        {"source_value": "smoothness_mean", "value_name": "smoothness1"},
        {"source_value": "compactness_mean", "value_name": "compactness1"},
        {"source_value": "concavity_mean", "value_name": "concavity1"},
        {"source_value": "concave_points_mean", "value_name": "concave_points1"},
        {"source_value": "symmetry_mean", "value_name": "symmetry1"},
        {"source_value": "fractal_dimension_mean", "value_name": "fractal_dimension1"},
        {"source_value": "radius_se", "value_name": "radius2"},
        {"source_value": "texture_se", "value_name": "texture2"},
        {"source_value": "perimeter_se", "value_name": "perimeter2"},
        {"source_value": "area_se", "value_name": "area2"},
        {"source_value": "smoothness_se", "value_name": "smoothness2"},
        {"source_value": "compactness_se", "value_name": "compactness2"},
        {"source_value": "concavity_se", "value_name": "concavity2"},
        {"source_value": "concave_points_se", "value_name": "concave_points2"},
        {"source_value": "symmetry_se", "value_name": "symmetry2"},
        {"source_value": "fractal_dimension_se", "value_name": "fractal_dimension2"},
        {"source_value": "radius_worst", "value_name": "radius3"},
        {"source_value": "texture_worst", "value_name": "texture3"},
        {"source_value": "perimeter_worst", "value_name": "perimeter3"},
        {"source_value": "area_worst", "value_name": "area3"},
        {"source_value": "smoothness_worst", "value_name": "smoothness3"},
        {"source_value": "compactness_worst", "value_name": "compactness3"},
        {"source_value": "concavity_worst", "value_name": "concavity3"},
        {"source_value": "concave_points_worst", "value_name": "concave_points3"},
        {"source_value": "symmetry_worst", "value_name": "symmetry3"},
        {"source_value": "fractal_dimension_worst", "value_name": "fractal_dimension3"}
    ]
}


DIABETES_CONCEPT_START_ID = 2_000_000_031
DIABETES_CODE_SYSTEM = f"{FHIR_CUSTOM_CODE_SYSTEM_URI_BASE}cdc-diabetes-indicators"
DIABETES_DEFINITIONS = {
    "Observation": [
        {"source_value": "CholCheck", "value_name": "chol_check_last_5_years"},
        {"source_value": "Smoker", "value_name": "smoker_status"},
        {"source_value": "PhysActivity", "value_name": "phys_activity_last_30_days"},
        {"source_value": "Fruits", "value_name": "eats_fruit_daily"},
        {"source_value": "Veggies", "value_name": "eats_vegetables_daily"},
        {"source_value": "HvyAlcoholConsump", "value_name": "heavy_alcohol_consumer"},
        {"source_value": "AnyHealthcare", "value_name": "has_healthcare_coverage"},
        {"source_value": "NoDocbcCost", "value_name": "deferred_doctor_visit_due_to_cost"},
        {"source_value": "DiffWalk", "value_name": "has_difficulty_walking"},
        {"source_value": "GenHlth", "value_name": "general_health_scale_1_5"},
        {"source_value": "MentHlth", "value_name": "days_of_poor_mental_health"},
        {"source_value": "PhysHlth", "value_name": "days_of_poor_physical_health"},
        {"source_value": "Education", "value_name": "education_level_scale_1_6"},
        {"source_value": "Income", "value_name": "income_level_scale_1_8"}
    ],
    "Condition": [
        {"source_value": "Diabetes_012", "value_name": "diabetes_status"},
        {"source_value": "HighBP", "value_name": "high_blood_pressure_status"},
        {"source_value": "HighChol", "value_name": "high_cholesterol_status"},
        {"source_value": "Stroke", "value_name": "stroke_history"},
        {"source_value": "HeartDiseaseorAttack", "value_name": "heart_disease_or_attack_history"}
    ],
    "Measurement": [
        {"source_value": "BMI", "value_name": "body_mass_index"}
    ]
}
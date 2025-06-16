# =============================================================================
# This file contains standard definitions for terminology used in the project.
# SINGLE SOURCE OF TRUTH for terminology definitions
# It is necessary because most of the services use very specific terminology
# not defined in most of the standard vocabularies.
# This file represents the "shared knowledge" or "data dictionary"
# agreed upon by data stewards and development teams.
# =============================================================================

FHIR_CUSTOM_CODE_SYSTEM_BASE_URI = "http://agedap_medical.com/codes/"

ALL_DEFINITIONS = {
    "radius1": {"source_value": "radius_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000001},
    "texture1": {"source_value": "texture_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000002},
    "perimeter1": {"source_value": "perimeter_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000003},
    "area1": {"source_value": "area_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000004},
    "smoothness1": {"source_value": "smoothness_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000005},
    "compactness1": {"source_value": "compactness_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000006},
    "concavity1": {"source_value": "concavity_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000007},
    "concave_points1": {"source_value": "concave_points_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000008},
    "symmetry1": {"source_value": "symmetry_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000009},
    "fractal_dimension1": {"source_value": "fractal_dimension_mean", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000010},
    "radius2": {"source_value": "radius_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000011},
    "texture2": {"source_value": "texture_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000012},
    "perimeter2": {"source_value": "perimeter_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000013},
    "area2": {"source_value": "area_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000014},
    "smoothness2": {"source_value": "smoothness_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000015},
    "compactness2": {"source_value": "compactness_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000016},
    "concavity2": {"source_value": "concavity_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000017},
    "concave_points2": {"source_value": "concave_points_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000018},
    "symmetry2": {"source_value": "symmetry_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000019},
    "fractal_dimension2": {"source_value": "fractal_dimension_se", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000020},
    "radius3": {"source_value": "radius_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000021},
    "texture3": {"source_value": "texture_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000022},
    "perimeter3": {"source_value": "perimeter_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000023},
    "area3": {"source_value": "area_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000024},
    "smoothness3": {"source_value": "smoothness_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000025},
    "compactness3": {"source_value": "compactness_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000026},
    "concavity3": {"source_value": "concavity_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000027},
    "concave_points3": {"source_value": "concave_points_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000028},
    "symmetry3": {"source_value": "symmetry_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000029},
    "fractal_dimension3": {"source_value": "fractal_dimension_worst", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}breast-cancer-screening", "omop_concept_id": 2000000030},


    "chol_check_last_5_years": {"source_value": "CholCheck", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000031},
    "smoker_status": {"source_value": "Smoker", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000032},
    "phys_activity_last_30_days": {"source_value": "PhysActivity", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000033},
    "eats_fruit_daily": {"source_value": "Fruits", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000034},
    "eats_vegetables_daily": {"source_value": "Veggies", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000035},
    "heavy_alcohol_consumer": {"source_value": "HvyAlcoholConsump", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000036},
    "has_healthcare_coverage": {"source_value": "AnyHealthcare", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000037},
    "deferred_doctor_visit_due_to_cost": {"source_value": "NoDocbcCost", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000038},
    "general_health_scale_1_5": {"source_value": "GenHlth", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000039},
    "days_of_poor_mental_health": {"source_value": "MentHlth", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000040},
    "days_of_poor_physical_health": {"source_value": "PhysHlth", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000041},
    "has_difficulty_walking": {"source_value": "DiffWalk", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000042},
    "patient_sex": {"source_value": "Sex", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "is_person_demographic": True, "omop_concept_id": 2000000043},
    "patient_age": {"source_value": "Age", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "is_person_demographic": True, "omop_concept_id": 2000000044},
    "education_level_scale_1_6": {"source_value": "Education", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000045},
    "income_level_scale_1_8": {"source_value": "Income", "domain": "Observation", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000046},
    
    # Condiciones
    "diabetes_status": {"source_value": "Diabetes_012", "domain": "Condition", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000047},
    "high_blood_pressure_status": {"source_value": "HighBP", "domain": "Condition", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000048},
    "high_cholesterol_status": {"source_value": "HighChol", "domain": "Condition", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000049},
    "stroke_history": {"source_value": "Stroke", "domain": "Condition", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000050},
    "heart_disease_or_attack_history": {"source_value": "HeartDiseaseorAttack", "domain": "Condition", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000051},
    
    # Medición
    "body_mass_index": {"source_value": "BMI", "domain": "Measurement", "fhir_system": f"{FHIR_CUSTOM_CODE_SYSTEM_BASE_URI}cdc-diabetes-indicators", "omop_concept_id": 2000000052}
}


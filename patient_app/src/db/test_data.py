import sys
import os
from datetime import date, datetime

# Adjust path to import from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from standard_definitions.terminology_definitions import ALL_DEFINITIONS
# Import session management like custom_concepts.py does
from config import get_session 
from omopmodel import OMOP_5_4_declarative as omop54

# --- Single Test Patient Configuration ---
PRIMARY_TEST_PERSON_ID = 758718
PRIMARY_TEST_PERSON_SOURCE_VALUE = "TestPatient_Alice_Primary"

# Comprehensive data for the primary test patient
# Keys are 'source_value' from ALL_DEFINITIONS
PRIMARY_PATIENT_SPECIFIC_DATA = {
    # Diabetes Indicators
    "CholCheck": 1.0, "Smoker": 0.0, "PhysActivity": 1.0, "Fruits": 1.0, "Veggies": 1.0,
    "HvyAlcoholConsump": 0.0, "AnyHealthcare": 1.0, "NoDocbcCost": 0.0,
    "GenHlth": 2.0, "MentHlth": 3.0, "PhysHlth": 1.0, "DiffWalk": 0.0,
    "Education": 5.0, "Income": 7.0, "BMI": 22.5,
    "Diabetes_012": 1.0, "HighBP": 0.0, "HighChol": 1.0, "Stroke": 0.0, "HeartDiseaseorAttack": 0.0,
    # Breast Cancer Screening Measurements
    "radius_mean": 17.99, "texture_mean": 10.38, "perimeter_mean": 122.8, "area_mean": 1001.0,
    "smoothness_mean": 0.1184, "compactness_mean": 0.2776, "concavity_mean": 0.3001,
    "concave_points_mean": 0.1471, "symmetry_mean": 0.2419, "fractal_dimension_mean": 0.07871,
    "radius_se": 1.095, "texture_se": 0.9053, "perimeter_se": 8.589, "area_se": 153.4,
    "smoothness_se": 0.006399, "compactness_se": 0.04904, "concavity_se": 0.05373,
    "concave_points_se": 0.01587, "symmetry_se": 0.03003, "fractal_dimension_se": 0.006193,
    "radius_worst": 25.38, "texture_worst": 17.33, "perimeter_worst": 184.6, "area_worst": 2019.0,
    "smoothness_worst": 0.1622, "compactness_worst": 0.6656, "concavity_worst": 0.7119,
    "concave_points_worst": 0.2654, "symmetry_worst": 0.4601, "fractal_dimension_worst": 0.1189
}

# Generic fallback values if a key is NOT in PRIMARY_PATIENT_SPECIFIC_DATA
# This ensures every item in ALL_DEFINITIONS gets some value if not specified above.
# For a single, fully defined test patient, PRIMARY_PATIENT_SPECIFIC_DATA should ideally cover all.
DEFAULT_FALLBACK_VALUES = {
    # Diabetes defaults (if not in PRIMARY_PATIENT_SPECIFIC_DATA)
    "CholCheck": 0.0, "Smoker": 0.0, "PhysActivity": 0.0, "Fruits": 0.0, "Veggies": 0.0,
    "HvyAlcoholConsump": 0.0, "AnyHealthcare": 0.0, "NoDocbcCost": 0.0,
    "GenHlth": 3.0, "MentHlth": 0.0, "PhysHlth": 0.0, "DiffWalk": 0.0,
    "Education": 1.0, "Income": 1.0, "BMI": 20.0,
    "Diabetes_012": 0.0, "HighBP": 0.0, "HighChol": 0.0, "Stroke": 0.0, "HeartDiseaseorAttack": 0.0,
    # Breast cancer defaults (if not in PRIMARY_PATIENT_SPECIFIC_DATA)
    "radius_mean": 10.0, "texture_mean": 10.0, "perimeter_mean": 50.0, "area_mean": 300.0,
    "smoothness_mean": 0.05, "compactness_mean": 0.05, "concavity_mean": 0.05,
    "concave_points_mean": 0.02, "symmetry_mean": 0.1, "fractal_dimension_mean": 0.05,
    "radius_se": 0.1, "texture_se": 0.1, "perimeter_se": 1.0, "area_se": 10.0,
    "smoothness_se": 0.001, "compactness_se": 0.005, "concavity_se": 0.005,
    "concave_points_se": 0.002, "symmetry_se": 0.005, "fractal_dimension_se": 0.001,
    "radius_worst": 12.0, "texture_worst": 12.0, "perimeter_worst": 60.0, "area_worst": 400.0,
    "smoothness_worst": 0.07, "compactness_worst": 0.07, "concavity_worst": 0.07,
    "concave_points_worst": 0.03, "symmetry_worst": 0.15, "fractal_dimension_worst": 0.06
}
# --- End Single Test Patient Configuration ---

def create_primary_person():
    """Create primary test person using SQLAlchemy session like custom_concepts.py"""
    person_data = {
        "person_id": PRIMARY_TEST_PERSON_ID,
        "gender_concept_id": 8532,  # female
        "year_of_birth": 1975,
        "month_of_birth": 5,
        "day_of_birth": 15,
        "birth_datetime": datetime(1975, 5, 15),
        "race_concept_id": 0,
        "ethnicity_concept_id": 0,
        "person_source_value": PRIMARY_TEST_PERSON_SOURCE_VALUE,
        "gender_source_value": "female"
    }
    
    with get_session() as session:
        # Check if person already exists
        existing = session.query(omop54.Person).filter_by(person_id=PRIMARY_TEST_PERSON_ID).first()
        if existing:
            print(f"Person with ID {PRIMARY_TEST_PERSON_ID} already exists.")
            return PRIMARY_TEST_PERSON_ID
        
        # Create new person
        person = omop54.Person(**person_data)
        session.add(person)
        session.commit()
        print(f"Created primary test person with ID: {PRIMARY_TEST_PERSON_ID}")
        return PRIMARY_TEST_PERSON_ID

def populate_all_patient_data(person_id, patient_specific_data):
    """Populate patient data using SQLAlchemy session like custom_concepts.py"""
    
    record_date = date.today()
    record_datetime = datetime.now()
    
    # OMOP Type Concept IDs
    measurement_type_concept_id = 32817  # Lab result
    observation_type_concept_id = 38000280  # Observation from EHR
    condition_type_concept_id = 38000175  # EHR condition
    
    print(f"\nPopulating all data for person_id {person_id}...")
    
    measurements_to_add = []
    observations_to_add = []
    conditions_to_add = []
    
    with get_session() as session:
        for value_name, definition in ALL_DEFINITIONS.items():
            source_value = definition["source_value"]
            domain = definition["domain"]
            concept_id = definition.get("omop_concept_id")
            
            if not concept_id:
                print(f"Warning: No OMOP concept ID for '{value_name}'. Skipping.")
                continue
            
            # Skip demographic data
            if definition.get("is_person_demographic", False):
                continue
            
            # Get data value
            data_value = patient_specific_data.get(source_value, DEFAULT_FALLBACK_VALUES.get(source_value))
            if data_value is None:
                print(f"Warning: No value found for '{source_value}'. Skipping.")
                continue
            
            print(f"  Processing: {source_value} -> {data_value} (domain: {domain})")
            
            try:
                if domain == "Measurement":
                    measurement_data = {
                        "person_id": person_id,
                        "measurement_concept_id": concept_id,
                        "measurement_date": record_date,
                        "measurement_datetime": record_datetime,
                        "measurement_type_concept_id": measurement_type_concept_id,
                        "value_as_number": float(data_value),
                        "measurement_source_value": source_value,
                        "measurement_source_concept_id": concept_id
                    }
                    measurements_to_add.append(omop54.Measurement(**measurement_data))
                
                elif domain == "Observation":
                    observation_data = {
                        "person_id": person_id,
                        "observation_concept_id": concept_id,
                        "observation_date": record_date,
                        "observation_datetime": record_datetime,
                        "observation_type_concept_id": observation_type_concept_id,
                        "value_as_number": float(data_value),
                        "observation_source_value": source_value,
                        "observation_source_concept_id": concept_id
                    }
                    observations_to_add.append(omop54.Observation(**observation_data))
                
                elif domain == "Condition":
                    if float(data_value) == 1.0:  # Only insert if condition is present
                        condition_data = {
                            "person_id": person_id,
                            "condition_concept_id": concept_id,
                            "condition_start_date": record_date,
                            "condition_start_datetime": record_datetime,
                            "condition_type_concept_id": condition_type_concept_id,
                            "condition_source_value": source_value,
                            "condition_source_concept_id": concept_id
                        }
                        conditions_to_add.append(omop54.ConditionOccurrence(**condition_data))
                    else:
                        print(f"    Skipping condition {source_value} (value: {data_value})")
                
                else:
                    print(f"    Unknown domain '{domain}' for {source_value}")
                    
            except Exception as e:
                print(f"    Error preparing {source_value}: {e}")
        
        # Bulk insert like custom_concepts.py does
        try:
            if measurements_to_add:
                session.add_all(measurements_to_add)
                print(f"  Added {len(measurements_to_add)} measurements")
            
            if observations_to_add:
                session.add_all(observations_to_add)
                print(f"  Added {len(observations_to_add)} observations")
            
            if conditions_to_add:
                session.add_all(conditions_to_add)
                print(f"  Added {len(conditions_to_add)} conditions")
            
            session.commit()
            print(f"✓ Successfully committed all data for person {person_id}")
            
        except Exception as e:
            print(f"✗ Error committing data: {e}")
            session.rollback()

def main():
    print(f"--- Running test_data.py ---")
    
    print("\nStep 1: Creating primary test person...")
    primary_person_id = create_primary_person()
    
    print(f"\nStep 2: Populating data for primary test person (ID: {primary_person_id})...")
    populate_all_patient_data(primary_person_id, PRIMARY_PATIENT_SPECIFIC_DATA)
    
    print("\n--- Finished test_data.py ---")

if __name__ == "__main__":
    main()

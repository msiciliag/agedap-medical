import sys
import os
import sqlite3
from datetime import date, datetime
import random


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from standard_definitions.terminology_definitions import (
    BREAST_CANCER_DEFINITIONS,
    DIABETES_DEFINITIONS,
    OMOP_CUSTOM_CONCEPT_START_ID
)

DB_PATH = os.path.join(os.path.dirname(__file__), 'omop_cdm.db')
VOCABULARY_ID_CUSTOM = 'AGEDAP_Medical_Custom' 
CONCEPT_CLASS_ID_CUSTOM = 'Clinical Finding'

current_concept_id_tracker = OMOP_CUSTOM_CONCEPT_START_ID

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_concept(conn, concept_id, concept_name, domain_id, concept_code, vocabulary_id=VOCABULARY_ID_CUSTOM, concept_class_id=CONCEPT_CLASS_ID_CUSTOM):
    cursor = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")
    far_future_str = "2099-12-31"
    try:
        cursor.execute("""
            INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept, concept_code, valid_start_date, valid_end_date, invalid_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, 'S', concept_code, today_str, far_future_str, None))
        # print(f"Inserted concept: {concept_name} (ID: {concept_id})")
    except sqlite3.IntegrityError:
        # This can happen if concept_id or (concept_code, vocabulary_id) is not unique.
        # The check before calling this function should prevent most of these for concept_code.
        print(f"Concept {concept_name} (ID: {concept_id}) or code {concept_code} likely already exists or other integrity violation.")
    return concept_id

def populate_concepts(conn):
    global current_concept_id_tracker
    created_concepts_map = {}  # To store source_value -> concept_id mapping

    # Breast Cancer Measurement Concepts
    domain_bc = "Measurement"
    for item in BREAST_CANCER_DEFINITIONS.get(domain_bc, []):
        concept_name = item["source_value"].replace("_", " ").title()
        concept_code = item["source_value"]
        
        cursor = conn.cursor()
        cursor.execute("SELECT concept_id FROM concept WHERE concept_code = ? AND vocabulary_id = ?", (concept_code, VOCABULARY_ID_CUSTOM))
        existing = cursor.fetchone()
        
        if existing:
            created_concepts_map[concept_code] = existing['concept_id']
            # print(f"Concept '{concept_name}' with code '{concept_code}' already exists with ID {existing['concept_id']}.")
        else:
            cid = create_concept(conn, current_concept_id_tracker, concept_name, domain_bc, concept_code)
            created_concepts_map[concept_code] = cid
            current_concept_id_tracker += 1

    # Diabetes Concepts
    for domain_dia, definitions in DIABETES_DEFINITIONS.items():
        for item in definitions:
            concept_name = item["source_value"].replace("_", " ").title()
            concept_code = item["source_value"]

            cursor = conn.cursor()
            cursor.execute("SELECT concept_id FROM concept WHERE concept_code = ? AND vocabulary_id = ?", (concept_code, VOCABULARY_ID_CUSTOM))
            existing = cursor.fetchone()

            if existing:
                created_concepts_map[concept_code] = existing['concept_id']
                # print(f"Concept '{concept_name}' with code '{concept_code}' already exists with ID {existing['concept_id']}.")
            else:
                cid = create_concept(conn, current_concept_id_tracker, concept_name, domain_dia.title(), concept_code)
                created_concepts_map[concept_code] = cid
                current_concept_id_tracker += 1
    
    conn.commit()
    print(f"Finished populating/verifying concepts. Next available concept_id for new custom concepts: {current_concept_id_tracker}")
    return created_concepts_map

def create_persons(conn):
    persons_data = [
        (1, 8532, 1975, 5, 15, "Patient_Alice_BC", "female"), 
        (2, 8507, 1988, 8, 22, "Patient_Bob_Diabetes", "male"),
        (3, 8532, 1970, 1, 1, "Patient_842302_BC", "female"),
    ]
    cursor = conn.cursor()
    person_ids = []
    for p_data in persons_data:
        person_id, gender_concept_id, year, month, day, source_val, gender_source_val = p_data
        try:
            birth_dt_str = datetime(year, month, day).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO person (person_id, gender_concept_id, year_of_birth, month_of_birth, day_of_birth, birth_datetime, race_concept_id, ethnicity_concept_id, person_source_value, gender_source_value)
                VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
            """, (person_id, gender_concept_id, year, month, day, birth_dt_str, source_val, gender_source_val))
            person_ids.append(person_id)
        except sqlite3.IntegrityError:
            # print(f"Person with ID {person_id} likely already exists.")
            person_ids.append(person_id) 
    conn.commit()
    print(f"Created/verified persons with IDs: {person_ids}")
    return person_ids

def populate_breast_cancer_measurements(conn, person_id, concepts_map, specific_measurements_data=None):
    cursor = conn.cursor()
    measurement_date_str = date.today().strftime("%Y-%m-%d")
    measurement_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    measurement_type_concept_id = 32817  # Example: Lab result

    for item in BREAST_CANCER_DEFINITIONS.get("Measurement", []):
        source_value = item["source_value"]
        measurement_concept_id = concepts_map.get(source_value)
        if not measurement_concept_id:
            print(f"Warning: Concept ID for '{source_value}' not found. Skipping measurement.")
            continue
        
        if specific_measurements_data and source_value in specific_measurements_data:
            value_as_number = specific_measurements_data[source_value]
        else:
            # Fallback to random data if not provided or for other persons (e.g. Alice)
            value_as_number = round(random.uniform(0.01, item.get("example_max", 50.0)), 4)
        
        try:
            cursor.execute("""
                INSERT INTO measurement (person_id, measurement_concept_id, measurement_date, measurement_datetime, measurement_type_concept_id, value_as_number, measurement_source_value, measurement_source_concept_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (person_id, measurement_concept_id, measurement_date_str, measurement_datetime_str, measurement_type_concept_id, value_as_number, source_value, measurement_concept_id))
        except sqlite3.IntegrityError as e:
            print(f"Error inserting measurement for {source_value}, person {person_id}: {e}")
    conn.commit()
    print(f"Populated breast cancer measurements for person_id {person_id}")


def main():
    conn = get_db_connection()
    
    print("Populating custom concepts...")
    created_concepts_map = populate_concepts(conn)
    
    print("\nCreating persons...")
    person_ids = create_persons(conn)

    if not person_ids:
        print("No persons created or found. Exiting.")
        conn.close()
        return

    # Data for Patient ID 842302
    patient_842302_data = {
        "radius_mean": 17.99,
        "texture_mean": 10.38,
        "perimeter_mean": 122.8,
        "area_mean": 1001.0,
        "smoothness_mean": 0.1184,
        "compactness_mean": 0.2776,
        "concavity_mean": 0.3001,
        "concave_points_mean": 0.1471,
        "symmetry_mean": 0.2419,
        "fractal_dimension_mean": 0.07871,
        "radius_se": 1.095,
        "texture_se": 0.9053,
        "perimeter_se": 8.589,
        "area_se": 153.4,
        "smoothness_se": 0.006399,
        "compactness_se": 0.04904,
        "concavity_se": 0.05373,
        "concave_points_se": 0.01587,
        "symmetry_se": 0.03003,
        "fractal_dimension_se": 0.006193,
        "radius_worst": 25.38,
        "texture_worst": 17.33,
        "perimeter_worst": 184.6,
        "area_worst": 2019.0,
        "smoothness_worst": 0.1622,
        "compactness_worst": 0.6656,
        "concavity_worst": 0.7119,
        "concave_points_worst": 0.2654,
        "symmetry_worst": 0.4601,
        "fractal_dimension_worst": 0.1189
    }

    if 1 in person_ids:
        print(f"\nPopulating breast cancer measurements for person_id 1 (Alice) with random data...")
        populate_breast_cancer_measurements(conn, 1, created_concepts_map)
    
    if 3 in person_ids: # For Patient 842302
        print(f"\nPopulating breast cancer measurements for person_id 3 (Patient 842302) with specific data...")
        populate_breast_cancer_measurements(conn, 3, created_concepts_map, specific_measurements_data=patient_842302_data)

    conn.close()
    print("\nFinished populating example OMOP data.")

if __name__ == "__main__":
    main()

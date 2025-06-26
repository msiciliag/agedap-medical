"""
Test script to verify database access and data retrieval for OMOP CDM tables.
Compares direct SQLite access with access through utils.db functions.
Accesses 1 of each custom concept defined in terminology_definitions.py.
"""
import sys
import os
import sqlite3
import logging

# Adjust path to import project modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from utils import db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../standard_definitions')))
from terminology_definitions import ALL_DEFINITIONS

logger = logging.getLogger(__name__)

def test_db_access():
    person_id = 758718
    concept_ids = None 

    logger.info("Testing get_patient_measurements (utils.db)...")
    measurements = db.get_patient_measurements(person_id, concept_ids)
    logger.info(f"Measurements (utils.db): {measurements}")

    logger.info("Testing get_patient_observations (utils.db)...")
    observations = db.get_patient_observations(person_id, concept_ids)
    logger.info(f"Observations (utils.db): {observations}")

    logger.info("Testing get_patient_conditions (utils.db)...")
    conditions = db.get_patient_conditions(person_id, concept_ids)
    logger.info(f"Conditions (utils.db): {conditions}")

    # Direct SQLite access
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/db/omop_cdm.db'))
    logger.info(f"\nDirect SQLite access to: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for table in ["measurement", "observation", "condition_occurrence"]:
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE person_id = ?", (person_id,))
            rows = cursor.fetchall()
            logger.info(f"{table.title()} (direct): {rows}")
        except Exception as e:
            logger.error(f"Error querying {table}: {e}")
    conn.close()

def test_custom_concepts_access():
    person_id = 758718
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/db/omop_cdm.db'))
    logger.info(f"\nTesting access for custom concepts for person_id={person_id}\n")
    # Group concepts by domain
    concepts_by_domain = {"Measurement": [], "Observation": [], "Condition": []}
    for key, val in ALL_DEFINITIONS.items():
        domain = val.get("domain")
        if domain in concepts_by_domain:
            concepts_by_domain[domain].append((key, val["omop_concept_id"]))
    # For each domain, try to access 1 concept
    for domain, concepts in concepts_by_domain.items():
        if not concepts:
            continue
        concept_key, concept_id = concepts[0]
        logger.info(f"Domain: {domain}, Concept: {concept_key}, Concept ID: {concept_id}")
        if domain == "Measurement":
            result = db.get_patient_measurements(person_id, [concept_id])
        elif domain == "Observation":
            result = db.get_patient_observations(person_id, [concept_id])
        elif domain == "Condition":
            result = db.get_patient_conditions(person_id, [concept_id])
        else:
            result = None
        logger.info(f"utils.db result: {result}")
        # Direct SQLite access
        table = domain.lower() if domain != "Condition" else "condition_occurrence"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE person_id = ? AND "+
                ("measurement_concept_id" if domain=="Measurement" else "observation_concept_id" if domain=="Observation" else "condition_concept_id")+
                " = ?", (person_id, concept_id))
            rows = cursor.fetchall()
            logger.info(f"Direct DB result: {rows}\n")
        except Exception as e:
            logger.error(f"Error querying {table}: {e}\n")
        conn.close()

def main():
    test_db_access()
    test_custom_concepts_access()

if __name__ == "__main__":
    main()

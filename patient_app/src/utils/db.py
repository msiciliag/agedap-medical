"""
Database operations layer for OMOP CDM.
Handles all CRUD operations, data loading, and database queries.
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import logging
from datetime import datetime, date

from db.db_init import schema_manager
from omopmodel import OMOP_5_4_declarative as omop54

logger = logging.getLogger(__name__)

@contextmanager
def get_db_session():
    """
    Get a database session with proper cleanup.
    """
    session = schema_manager.SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def get_gender(patient_id: int) -> Optional[str]:
    """Get patient's gender by ID."""
    try:
        with get_db_session() as session:
            patient = session.query(omop54.Person).filter(
                omop54.Person.person_id == patient_id
            ).first()
            if patient:
                return patient.gender_source_value
    except Exception as e:
        logger.error(f"Error fetching gender for patient {patient_id}: {e}")
    return None

def get_date_of_birth(patient_id: int) -> Optional[str]:
    """Get patient's date of birth by ID."""
    try:
        with get_db_session() as session:
            patient = session.query(omop54.Person).filter(
                omop54.Person.person_id == patient_id
            ).first()
            year_of_birth = patient.year_of_birth
            month_of_birth = patient.month_of_birth
            day_of_birth = patient.day_of_birth
            if year_of_birth is not None and month_of_birth is not None and day_of_birth is not None:
                return date(year_of_birth, month_of_birth, day_of_birth)
    except Exception as e:
        logger.error(f"Error fetching date of birth for patient {patient_id}: {e}")
    return None

def get_patient_measurements(
    patient_id: int, 
    concept_ids: List[int] = None,
    limit: int = 100
) -> List[omop54.Measurement]:
    """Get measurements for a patient."""
    try:
        with get_db_session() as session:
            query = session.query(omop54.Measurement).filter(
                omop54.Measurement.person_id == patient_id
            )
            
            if concept_ids:
                query = query.filter(omop54.Measurement.measurement_concept_id.in_(concept_ids))
                
            return query.order_by(omop54.Measurement.measurement_datetime.desc()).limit(limit).all()
    except Exception as e:
        logger.error(f"Error fetching measurements for patient {patient_id}: {e}")
        return []

def get_concept_by_id(concept_id: int) -> Optional[omop54.Concept]:
    """Get a concept by ID."""
    try:
        with get_db_session() as session:
            return session.query(omop54.Concept).filter(
                omop54.Concept.concept_id == concept_id
            ).first()
    except Exception as e:
        logger.error(f"Error fetching concept {concept_id}: {e}")
        return None

def clear_database():
    """Deletes all entries in the OMOP database and reloads the definitions."""
    try:
        with get_db_session() as session:
            # Clear all tables in the OMOP schema
            session.query(omop54.ConditionOccurrence).delete()
            session.query(omop54.Measurement).delete()
            session.query(omop54.Observation).delete()
            session.query(omop54.Concept).delete()
            session.query(omop54.Person).delete()
            session.commit()
            logger.info("Database cleared successfully.")
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise
    
def get_patient_observations(
    patient_id: int,
    concept_ids: List[int] = None,
    limit: int = 100
) -> List[omop54.Observation]:
    """Get observations for a patient."""
    try:
        with get_db_session() as session:
            query = session.query(omop54.Observation).filter(
                omop54.Observation.person_id == patient_id
            )
            
            if concept_ids:
                query = query.filter(omop54.Observation.observation_concept_id.in_(concept_ids))
                
            return query.order_by(omop54.Observation.observation_datetime.desc()).limit(limit).all()
    except Exception as e:
        logger.error(f"Error fetching observations for patient {patient_id}: {e}")
        return []

def get_patient_conditions(
    patient_id: int,
    concept_ids: List[int] = None,
    limit: int = 100
) -> List[omop54.ConditionOccurrence]:
    """Get conditions for a patient."""
    try:
        with get_db_session() as session:
            query = session.query(omop54.ConditionOccurrence).filter(
                omop54.ConditionOccurrence.person_id == patient_id
            )
            
            if concept_ids:
                query = query.filter(omop54.ConditionOccurrence.condition_concept_id.in_(concept_ids))
                
            return query.order_by(omop54.ConditionOccurrence.condition_start_date.desc()).limit(limit).all()
    except Exception as e:
        logger.error(f"Error fetching conditions for patient {patient_id}: {e}")
        return []

def get_person_by_id(person_id: int) -> Optional[omop54.Person]:
    """Get person by ID."""
    try:
        with get_db_session() as session:
            return session.query(omop54.Person).filter(
                omop54.Person.person_id == person_id
            ).first()
    except Exception as e:
        logger.error(f"Error fetching person {person_id}: {e}")
        return None

# ===== DATA LOADING FUNCTIONS =====

def bulk_insert_conditions(conditions_data: List[dict]):
    """Bulk insert conditions."""
    try:
        with get_db_session() as session:
            conditions = [omop54.ConditionOccurrence(**data) for data in conditions_data]
            session.add_all(conditions)
            logger.info(f"Inserted {len(conditions)} conditions")
    except Exception as e:
        logger.error(f"Error bulk inserting conditions: {e}")
        raise
    
def bulk_insert_measurements(measurements_data: List[dict]):
    """Bulk insert measurements."""
    try:
        with get_db_session() as session:
            measurements = [omop54.Measurement(**data) for data in measurements_data]
            session.add_all(measurements)
            logger.info(f"Inserted {len(measurements)} measurements")
    except Exception as e:
        logger.error(f"Error bulk inserting measurements: {e}")
        raise

def bulk_insert_observations(observations_data: List[dict]):
    """Bulk insert observations."""
    try:
        with get_db_session() as session:
            observations = [omop54.Observation(**data) for data in observations_data]
            session.add_all(observations)
            logger.info(f"Inserted {len(observations)} observations")
    except Exception as e:
        logger.error(f"Error bulk inserting observations: {e}")
        raise

def bulk_insert_concepts(concepts_data: List[dict]):
    """Bulk insert concepts."""
    try:
        with get_db_session() as session:
            concepts = [omop54.Concept(**data) for data in concepts_data]
            session.add_all(concepts)
            logger.info(f"Inserted {len(concepts)} concepts")
    except Exception as e:
        logger.error(f"Error bulk inserting concepts: {e}")
        raise

def get_database_stats() -> Dict[str, Any]:
    """Get comprehensive database statistics."""
    return {
        'schema_valid': schema_manager.validate_schema()['valid'],
        'table_counts': schema_manager.get_table_counts()
    }

def create_or_update_person(person_omop_data: Dict[str, Any]) -> Optional[omop54.Person]:
    """
    Creates a new person record if one doesn't exist, 
    or updates an existing one based on person_id.
    """
    if 'person_id' not in person_omop_data or person_omop_data['person_id'] is None:
        logger.error("person_id is required in person_omop_data for create_or_update_person.")
        return None

    # Map gender string to OMOP concept_id if needed
    if "gender_concept_id" not in person_omop_data or person_omop_data["gender_concept_id"] is None:
        gender_str = str(person_omop_data.get("gender_source_value", "")).lower()
        if gender_str == "female":
            person_omop_data["gender_concept_id"] = 8532
        elif gender_str == "male":
            person_omop_data["gender_concept_id"] = 8507
        else:
            person_omop_data["gender_concept_id"] = 0

    person_id = person_omop_data['person_id']

    try:
        with get_db_session() as session:
            person = session.query(omop54.Person).filter(omop54.Person.person_id == person_id).first()

            if person:
                logger.info(f"Updating existing person record for ID {person_id}")
                for key, value in person_omop_data.items():
                    if hasattr(person, key):
                        setattr(person, key, value)
                    else:
                        logger.warning(f"Attribute {key} not found on Person model during update.")
            else:
                # Create new person
                logger.info(f"Creating new person record for ID {person_id}")
                new_person = omop54.Person(**person_omop_data)
                session.add(new_person)
                person = new_person
            
            session.flush() # Ensure person object is populated, e.g., with defaults from DB

    except Exception as e:
        logger.error(f"Error creating or updating person with ID {person_id}: {e}")
        return None

# Backward compatibility functions
def get_session():
    """Backward compatibility with old config.py"""
    return schema_manager.SessionLocal()
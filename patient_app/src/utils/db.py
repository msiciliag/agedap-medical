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

class DatabaseManager:
    """
    Enhanced database manager for OMOP CDM operations.
    Maintains full backward compatibility while adding new functionality.
    """
    
    @staticmethod
    @contextmanager
    def get_db_session():
        """
        Get a database session with proper cleanup.
        MAINTAINS BACKWARD COMPATIBILITY with existing code.
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
    
    # ===== EXISTING METHODS - UNCHANGED for backward compatibility =====
    
    @staticmethod
    def get_patient_measurements(
        patient_id: int, 
        concept_ids: List[int] = None,
        limit: int = 100
    ) -> List[omop54.Measurement]:
        """Get measurements for a patient. UNCHANGED."""
        try:
            with DatabaseManager.get_db_session() as session:
                query = session.query(omop54.Measurement).filter(
                    omop54.Measurement.person_id == patient_id
                )
                
                if concept_ids:
                    query = query.filter(omop54.Measurement.measurement_concept_id.in_(concept_ids))
                    
                return query.order_by(omop54.Measurement.measurement_datetime.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching measurements for patient {patient_id}: {e}")
            return []
    
    @staticmethod
    def get_concept_by_id(concept_id: int) -> Optional[omop54.Concept]:
        """Get a concept by ID. UNCHANGED."""
        try:
            with DatabaseManager.get_db_session() as session:
                return session.query(omop54.Concept).filter(
                    omop54.Concept.concept_id == concept_id
                ).first()
        except Exception as e:
            logger.error(f"Error fetching concept {concept_id}: {e}")
            return None

    @staticmethod
    def clear_database():
        """Clear the database. ENHANCED but maintains interface."""
        try:
            logger.info("Clearing database...")
            schema_manager.drop_schema()
            logger.info("  Database cleared successfully")
        except Exception as e:
            logger.error(f" Error clearing database: {e}")
            raise
    
    # ===== NEW ENHANCED METHODS =====
    
    @staticmethod
    def get_patient_observations(
        patient_id: int,
        concept_ids: List[int] = None,
        limit: int = 100
    ) -> List[omop54.Observation]:
        """Get observations for a patient."""
        try:
            with DatabaseManager.get_db_session() as session:
                query = session.query(omop54.Observation).filter(
                    omop54.Observation.person_id == patient_id
                )
                
                if concept_ids:
                    query = query.filter(omop54.Observation.observation_concept_id.in_(concept_ids))
                    
                return query.order_by(omop54.Observation.observation_datetime.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching observations for patient {patient_id}: {e}")
            return []
    
    @staticmethod
    def get_patient_conditions(
        patient_id: int,
        concept_ids: List[int] = None,
        limit: int = 100
    ) -> List[omop54.ConditionOccurrence]:
        """Get conditions for a patient."""
        try:
            with DatabaseManager.get_db_session() as session:
                query = session.query(omop54.ConditionOccurrence).filter(
                    omop54.ConditionOccurrence.person_id == patient_id
                )
                
                if concept_ids:
                    query = query.filter(omop54.ConditionOccurrence.condition_concept_id.in_(concept_ids))
                    
                return query.order_by(omop54.ConditionOccurrence.condition_start_date.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching conditions for patient {patient_id}: {e}")
            return []
    
    @staticmethod
    def get_person_by_id(person_id: int) -> Optional[omop54.Person]:
        """Get person by ID."""
        try:
            with DatabaseManager.get_db_session() as session:
                return session.query(omop54.Person).filter(
                    omop54.Person.person_id == person_id
                ).first()
        except Exception as e:
            logger.error(f"Error fetching person {person_id}: {e}")
            return None
    
    @staticmethod
    def person_exists(person_id: int) -> bool:
        """Check if a person exists."""
        try:
            with DatabaseManager.get_db_session() as session:
                return session.query(omop54.Person).filter(
                    omop54.Person.person_id == person_id
                ).first() is not None
        except Exception as e:
            logger.error(f"Error checking person existence {person_id}: {e}")
            return False
    
    # ===== DATA LOADING METHODS =====
    
    @staticmethod
    def create_person(person_data: dict) -> int:
        """Create a new person record."""
        try:
            with DatabaseManager.get_db_session() as session:
                person = omop54.Person(**person_data)
                session.add(person)
                session.flush()  # Get the ID without committing
                return person.person_id
        except Exception as e:
            logger.error(f"Error creating person: {e}")
            raise
    
    @staticmethod
    def bulk_insert_measurements(measurements_data: List[dict]):
        """Bulk insert measurements."""
        try:
            with DatabaseManager.get_db_session() as session:
                measurements = [omop54.Measurement(**data) for data in measurements_data]
                session.add_all(measurements)
                logger.info(f"Inserted {len(measurements)} measurements")
        except Exception as e:
            logger.error(f"Error bulk inserting measurements: {e}")
            raise
    
    @staticmethod
    def bulk_insert_observations(observations_data: List[dict]):
        """Bulk insert observations."""
        try:
            with DatabaseManager.get_db_session() as session:
                observations = [omop54.Observation(**data) for data in observations_data]
                session.add_all(observations)
                logger.info(f"Inserted {len(observations)} observations")
        except Exception as e:
            logger.error(f"Error bulk inserting observations: {e}")
            raise
    
    @staticmethod
    def bulk_insert_concepts(concepts_data: List[dict]):
        """Bulk insert concepts."""
        try:
            with DatabaseManager.get_db_session() as session:
                concepts = [omop54.Concept(**data) for data in concepts_data]
                session.add_all(concepts)
                logger.info(f"Inserted {len(concepts)} concepts")
        except Exception as e:
            logger.error(f"Error bulk inserting concepts: {e}")
            raise
    
    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        return {
            'schema_valid': schema_manager.validate_schema()['valid'],
            'table_counts': schema_manager.get_table_counts()
        }

# Backward compatibility functions
def get_session():
    """Backward compatibility with old config.py"""
    return schema_manager.SessionLocal()
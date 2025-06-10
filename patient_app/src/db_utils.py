"""
Utilities for database operations using OMOP CDM, after initialization.
"""
from sqlalchemy.orm import Session
from typing import List, Optional

from patient_app.src.db.config import get_session 
from omopmodel import OMOP_5_4_declarative as omop54


class DatabaseManager:
    """Centralized manager for OMOP CDM database query operations."""
    
    @staticmethod
    def get_db_session() -> Session: 
        """Get a database session."""
        return get_session() 
        
    @staticmethod
    def get_patient_measurements(
        patient_id: int, 
        concept_ids: List[int] = None,
        limit: int = 100
    ) -> List[omop54.Measurement]:
        """Get measurements for a patient."""
        with DatabaseManager.get_db_session() as session:
            query = session.query(omop54.Measurement).filter(
                omop54.Measurement.person_id == patient_id
            )
            
            if concept_ids:
                query = query.filter(omop54.Measurement.measurement_concept_id.in_(concept_ids))
                
            return query.order_by(omop54.Measurement.measurement_datetime.desc()).limit(limit).all()
    
    @staticmethod
    def get_concept_by_id(concept_id: int) -> Optional[omop54.Concept]:
        """Get a concept by ID."""
        with DatabaseManager.get_db_session() as session:
            return session.query(omop54.Concept).filter(
                omop54.Concept.concept_id == concept_id
            ).first()





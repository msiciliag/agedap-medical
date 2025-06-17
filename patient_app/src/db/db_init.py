"""
Low-level database initialization and schema management.
Handles OMOP CDM schema creation, validation, and maintenance.
"""
import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from omopmodel import OMOP_5_4_declarative as omop54

logger = logging.getLogger(__name__)

class OMOPSchemaManager:
    """Low-level OMOP CDM schema management."""
    
    def __init__(self):
        self.database_url = os.environ.get(
            "DATABASE_URL", 
            "sqlite:////root/agedap-medical/patient_app/src/db/omop_cdm.db"
        )
        self.engine = create_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def create_schema(self):
        """Create all OMOP CDM tables."""
        try:
            logger.info("Creating OMOP CDM schema...")
            omop54.Base.metadata.create_all(self.engine)
            logger.info("OMOP CDM schema created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating OMOP schema: {e}")
            raise
    
    def drop_schema(self):
        """Drop all OMOP CDM tables."""
        try:
            logger.info("Dropping OMOP CDM schema...")
            omop54.Base.metadata.drop_all(self.engine)
            logger.info("OMOP CDM schema dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Error dropping OMOP schema: {e}")
            raise
    
    def reset_schema(self):
        """Drop and recreate the entire schema."""
        logger.info("Resetting OMOP CDM schema...")
        self.drop_schema()
        self.create_schema()
        logger.info("OMOP CDM schema reset complete")
    
    def schema_exists(self) -> bool:
        """Check if OMOP schema exists."""
        inspector = inspect(self.engine)
        return inspector.has_table("concept")
    
    def validate_schema(self) -> dict:
        """Validate schema integrity."""
        inspector = inspect(self.engine)
        required_tables = ['person', 'concept', 'measurement', 'observation', 'condition_occurrence']
        
        validation_result = {
            'valid': True,
            'missing_tables': [],
            'existing_tables': []
        }
        
        for table in required_tables:
            if inspector.has_table(table):
                validation_result['existing_tables'].append(table)
            else:
                validation_result['missing_tables'].append(table)
                validation_result['valid'] = False
        
        return validation_result
    
    def get_table_counts(self) -> dict:
        """Get record counts for all main tables."""
        counts = {}
        try:
            with self.SessionLocal() as session:
                counts['persons'] = session.query(omop54.Person).count()
                counts['concepts'] = session.query(omop54.Concept).count()
                counts['measurements'] = session.query(omop54.Measurement).count()
                counts['observations'] = session.query(omop54.Observation).count()
                counts['conditions'] = session.query(omop54.ConditionOccurrence).count()
        except Exception as e:
            logger.error(f"Error getting table counts: {e}")
        return counts

schema_manager = OMOPSchemaManager()

def create_omop_tables():
    """Create OMOP tables"""
    return schema_manager.create_schema()

def get_engine():
    """Get database engine."""
    return schema_manager.engine

def get_session_factory():
    """Get session factory."""
    return schema_manager.SessionLocal
"""
Application initialization module - Updated for new three-layer architecture.
"""
import os
import sys
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent 
project_root_parent = project_root.parent 
sys.path.insert(0, str(project_root_parent))

from db.db_init import schema_manager
from utils.omop import load_custom_concepts_from_definitions
from utils import db

def initialize_application(reset_db: bool = True):
    """
    Initialize the application with new three-layer architecture.
    
    Args:
        reset_db: If True, resets the database schema
    """
    logger.info("Initializing application with new architecture...")
    
    try:
        if reset_db:
            logger.info("Resetting database schema...")
            schema_manager.reset_schema()
        elif not schema_manager.schema_exists():
            logger.info("Creating database schema...")
            schema_manager.create_schema()
        else:
            logger.info("Database schema already exists")
        
        validation = schema_manager.validate_schema()
        if not validation['valid']:
            logger.error(f"Schema validation failed: {validation['missing_tables']}")
            raise Exception("Database schema is invalid")
        
        logger.info("Loading custom concepts...")
        load_custom_concepts_from_definitions()
        
        stats = db.get_database_stats()
        logger.info(f"Database statistics: {stats}")
        
        logger.info("  Application initialization complete")
    
    except Exception as e:
        logger.error(f" Application initialization failed: {e}")
        raise


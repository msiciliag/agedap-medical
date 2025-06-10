from patient_app.src.db.config import create_omop_tables, engine
from patient_app.src.db.loaders.custom_concepts import load_defined_custom_concepts
from sqlalchemy import inspect
import sys
from pathlib import Path
import logging # Added for logging

# Ensure standard_definitions can be found by adding the project root to sys.path
# This assumes omop_initializer.py is in patient_app/src/db/
# and standard_definitions is at the project root level /root/agedap-medical/
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__) # Create a logger for this module

def ensure_database_initialized():
    """
    Ensures the OMOP database schema is created and custom concepts are loaded.
    This function is idempotent.
    """
    logger.info("Ensuring database is initialized...")
    inspector = inspect(engine)
    
    if not inspector.has_table("concept"): 
        logger.info("Core OMOP tables not found. Creating schema...")
        create_omop_tables()
    else:
        logger.info("Core OMOP tables found.")

    load_defined_custom_concepts()
    
    logger.info("Database initialization check complete.")

if __name__ == '__main__':
    # Basic logging setup for direct script execution
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.info("Running OMOP Initializer directly...")
    ensure_database_initialized()
    logger.info("Manual initialization finished.")

"""
Application initialization module.
"""
import os
import sys
from pathlib import Path

# --- Logging Configuration ---
import logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
# --- End Logging Configuration ---

# --- Path Setup (Crucial for finding standard_definitions and other modules) ---
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent # /root/agedap-medical/patient_app
project_root_parent = project_root.parent # /root/agedap-medical/
sys.path.insert(0, str(project_root_parent))
# --- End Path Setup ---

from patient_app.src.db.omop_initializer import ensure_database_initialized

def initialize_application():
    """Initialize the application and its dependencies."""
    logger.info("Initializing application...")
    
    # Ensure DB is set up before the app fully starts or config is used
    ensure_database_initialized()

    logger.info("Application initialization complete.")

# Example of how it might be called if this is the main entry point for some setups
if __name__ == '__main__':
    initialize_application()

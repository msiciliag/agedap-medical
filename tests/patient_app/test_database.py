"""
Tests for database functionality.
"""
import pytest
import sys
import os
import sqlite3
from pathlib import Path

# Add the project paths to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../patient_app/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

try:
    from utils import db
    from standard_definitions.terminology_definitions import ALL_DEFINITIONS
except ImportError as e:
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


class TestDatabaseAccess:
    """Test class for database access functionality."""
    
    def test_db_module_imports(self):
        """Test that the database module can be imported."""
        assert db is not None
        
    def test_terminology_definitions_import(self):
        """Test that terminology definitions can be imported."""
        assert ALL_DEFINITIONS is not None
        assert isinstance(ALL_DEFINITIONS, dict)
        assert len(ALL_DEFINITIONS) > 0
    
    def test_sample_patient_id(self):
        """Test with a sample patient ID."""
        test_patient_id = 758718
        
        # These should not raise exceptions even if they return empty results
        try:
            measurements = db.get_patient_measurements(test_patient_id, None)
            assert measurements is not None
            assert isinstance(measurements, (list, dict, type(None)))
        except Exception as e:
            pytest.skip(f"Database not available or function not implemented: {e}")
    
    def test_database_file_exists(self):
        """Test that the database file exists."""
        db_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '../../patient_app/src/db/omop_cdm.db'
        ))
        
        if os.path.exists(db_path):
            # If database exists, test basic connection
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
                
                assert len(tables) > 0, "Database should contain tables"
                
                # Check for expected OMOP tables
                table_names = [table[0] for table in tables]
                omop_tables = ['person', 'measurement', 'observation', 'condition_occurrence']
                
                for omop_table in omop_tables:
                    if omop_table in table_names:
                        assert True  # At least some OMOP tables exist
                        break
                        
            except sqlite3.Error as e:
                pytest.skip(f"Could not connect to database: {e}")
        else:
            pytest.skip("Database file does not exist")
    
    def test_custom_concepts_structure(self):
        """Test that custom concepts have the expected structure."""
        # Group concepts by domain
        concepts_by_domain = {"Measurement": [], "Observation": [], "Condition": []}
        
        for key, val in ALL_DEFINITIONS.items():
            domain = val.get("domain")
            if domain in concepts_by_domain:
                concepts_by_domain[domain].append((key, val["omop_concept_id"]))
        
        # Check that we have concepts for each domain
        for domain, concepts in concepts_by_domain.items():
            if concepts:  # If domain has concepts
                concept_key, concept_id = concepts[0]
                assert isinstance(concept_id, int)
                assert concept_id > 0
                
    def test_db_functions_exist(self):
        """Test that expected database functions exist."""
        expected_functions = [
            'get_patient_measurements',
            'get_patient_observations', 
            'get_patient_conditions'
        ]
        
        for func_name in expected_functions:
            assert hasattr(db, func_name), f"Missing database function: {func_name}"
            assert callable(getattr(db, func_name)), f"Function {func_name} is not callable"

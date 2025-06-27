"""
Tests for terminology definitions.
"""
import pytest
import os
from pathlib import Path


def test_terminology_definitions_file_exists():
    """Test that terminology_definitions.py file exists."""
    definitions_path = Path(__file__).parent.parent.parent / "standard_definitions" / "terminology_definitions.py"
    assert definitions_path.exists(), "terminology_definitions.py should exist"


def test_terminology_definitions_content():
    """Test that terminology definitions file contains expected content."""
    definitions_path = Path(__file__).parent.parent.parent / "standard_definitions" / "terminology_definitions.py"
    
    if definitions_path.exists():
        content = definitions_path.read_text()
        
        # Check for main definitions
        assert "ALL_DEFINITIONS" in content, "ALL_DEFINITIONS should be defined"
        assert "FHIR_CUSTOM_CODE_SYSTEM_BASE_URI" in content, "FHIR base URI should be defined"
        
        # Check for breast cancer definitions
        breast_cancer_terms = [
            "radius1", "texture1", "perimeter1", "area1", "smoothness1"
        ]
        
        for term in breast_cancer_terms:
            assert term in content, f"Breast cancer term {term} should be defined"
            
        # Check for diabetes definitions  
        diabetes_terms = [
            "chol_check_last_5_years", "smoker_status", "phys_activity_last_30_days"
        ]
        
        for term in diabetes_terms:
            assert term in content, f"Diabetes term {term} should be defined"
            
        # Check for domain types
        domains = ["Measurement", "Observation"]
        for domain in domains:
            assert domain in content, f"Domain {domain} should be used"
            
        # Check that domain "Condition" might be used (optional)
        # This is flexible since not all projects use all domain types


def test_terminology_structure_validation():
    """Test that we can validate the terminology structure by parsing the file."""
    definitions_path = Path(__file__).parent.parent.parent / "standard_definitions" / "terminology_definitions.py"
    
    if definitions_path.exists():
        # Try to execute the file to validate syntax
        import sys
        sys.path.insert(0, str(definitions_path.parent))
        
        try:
            import terminology_definitions
            
            # Basic validation
            assert hasattr(terminology_definitions, 'ALL_DEFINITIONS')
            assert hasattr(terminology_definitions, 'FHIR_CUSTOM_CODE_SYSTEM_BASE_URI')
            
            all_defs = terminology_definitions.ALL_DEFINITIONS
            assert isinstance(all_defs, dict)
            assert len(all_defs) > 0
            
            # Check structure of first definition
            if all_defs:
                first_key = list(all_defs.keys())[0]
                first_def = all_defs[first_key]
                
                required_fields = ["source_value", "domain", "fhir_system", "omop_concept_id"]
                for field in required_fields:
                    assert field in first_def, f"Missing required field: {field}"
                    
        except ImportError as e:
            pytest.skip(f"Could not import terminology_definitions: {e}")
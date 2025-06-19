"""
High-level OMOP data processing and schema management.
Handles data formatting, schema validation, and business logic for ML models.
"""
import numpy as np
from datetime import datetime, date
from typing import Dict, Optional, Any, Tuple
import logging
import sys
from pathlib import Path

from utils import db
from omopmodel import OMOP_5_4_declarative as omop54
from datetime import date, datetime 

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from standard_definitions.terminology_definitions import ALL_DEFINITIONS
except ImportError:
    ALL_DEFINITIONS = {}
    logging.warning("Could not import ALL_DEFINITIONS")

logger = logging.getLogger(__name__)

def validate_schema(schema: Dict) -> Dict[str, Any]:
    """Validate a data extraction schema."""
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'feature_count': 0
    }
    
    if not isinstance(schema, dict):
        validation_result['valid'] = False
        validation_result['errors'].append("Schema must be a dictionary")
        return validation_result
    
    supported_domains = ['measurement', 'observation', 'condition']
    total_features = 0
    
    for domain, features in schema.items():
        if domain not in supported_domains:
            validation_result['warnings'].append(f"Unknown domain: {domain}")
            continue
            
        if not isinstance(features, list):
            validation_result['errors'].append(f"Domain {domain} must contain a list of features")
            validation_result['valid'] = False
            continue
        
        total_features += len(features)
        
        for feature in features:
            if not isinstance(feature, dict):
                validation_result['errors'].append(f"Feature in {domain} must be a dictionary")
                validation_result['valid'] = False
                continue
            
            required_keys = ['value_name']
            for key in required_keys:
                if key not in feature:
                    validation_result['errors'].append(f"Feature missing required key: {key}")
                    validation_result['valid'] = False
    
    validation_result['feature_count'] = total_features
    return validation_result

def _calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date."""
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def _map_age_to_uci_category(age: int) -> float:
    """Map raw age to UCI dataset age category (1-13)."""
    if 18 <= age <= 24: return 1.0
    elif 25 <= age <= 29: return 2.0
    elif 30 <= age <= 34: return 3.0
    elif 35 <= age <= 39: return 4.0
    elif 40 <= age <= 44: return 5.0
    elif 45 <= age <= 49: return 6.0
    elif 50 <= age <= 54: return 7.0
    elif 55 <= age <= 59: return 8.0
    elif 60 <= age <= 64: return 9.0
    elif 65 <= age <= 69: return 10.0
    elif 70 <= age <= 74: return 11.0
    elif 75 <= age <= 79: return 12.0
    elif age >= 80: return 13.0
    else: return 0.0

def _generate_mock_data(schema: Dict, person_id: Optional[int] = None) -> np.array:
    """Generate mock data for testing/fallback."""
    logger.info(f"Generating mock data for schema (person_id: {person_id})")
    
    mock_values = []
    
    # Determine processing order
    domain_processing_order = ["measurement", "condition", "observation"]
    if any(k in schema for k in ["observation", "condition"]):
        domain_processing_order = ["observation", "condition", "measurement"]
    elif "measurement" in schema:
        domain_processing_order = ["measurement"]
    
    for domain_key in domain_processing_order:
        if domain_key not in schema:
            continue
            
        features = schema[domain_key]
        for feature in features:
            value_name = feature.get('value_name', '').lower()
            is_demographic = feature.get("is_person_demographic", False)
            
            if is_demographic or value_name in ["patient_sex", "patient_age"]:
                if value_name == "patient_sex":
                    mock_values.append(float(np.random.randint(0, 2)))
                elif value_name == "patient_age":
                    mock_values.append(float(np.random.randint(1, 14)))
                else:
                    mock_values.append(0.0)
            elif domain_key == "condition":
                mock_values.append(float(np.random.randint(0, 2)))
            elif domain_key == "observation":
                # Heuristic for binary vs continuous
                if any(keyword in value_name for keyword in ["check", "smoker", "activity", "fruit", "vegetable"]):
                    mock_values.append(float(np.random.randint(0, 2)))
                else:
                    mock_values.append(round(np.random.uniform(0.0, 5.0), 4))
            else:  # measurement
                mock_values.append(round(np.random.uniform(10.0, 50.0), 4))
    
    return np.array([mock_values]) if mock_values else np.array([[]])

def extract_patient_data(schema: Dict, person_id: int) -> np.array:
    validation = validate_schema(schema)
    if not validation['valid']:
        logger.error(f"Schema validation failed: {validation['errors']}")
        return _generate_mock_data(schema, person_id)
    all_feature_values = []
    person_record_cache = None
    domain_processing_order = ["measurement", "condition", "observation"]
    if any(k in schema for k in ["observation", "condition"]):
        domain_processing_order = ["observation", "condition", "measurement"]
    elif "measurement" in schema:
        domain_processing_order = ["measurement"]
    try:
        for domain_key in domain_processing_order:
            if domain_key not in schema:
                continue
            feature_definitions = schema[domain_key]
            for feature_info in feature_definitions:
                value_name = feature_info.get('value_name', '')
                is_demographic = feature_info.get("is_person_demographic", False)
                # Handle demographic features
                if is_demographic or value_name in ["patient_sex", "patient_age"]:
                    if person_record_cache is None:
                        person_record_cache = db.get_person_by_id(person_id)
                    if not person_record_cache:
                        logger.warning(f"Person {person_id} not found for demographic feature {value_name}")
                        all_feature_values.append(0.0)
                        continue
                    if value_name == "patient_sex":
                        # OMOP: FEMALE = 8532, MALE = 8507
                        # UCI: 0 = female, 1 = male
                        value = 0.0 if person_record_cache.get("gender_concept_id") == 8532 else 1.0
                        all_feature_values.append(value)
                    elif value_name == "patient_age":
                        if person_record_cache.get("year_of_birth"):
                            try:
                                birth_date = datetime(
                                    person_record_cache.get("year_of_birth"),
                                    person_record_cache.get("month_of_birth") or 1,
                                    person_record_cache.get("day_of_birth") or 1
                                )
                                raw_age = _calculate_age(birth_date)
                                age_category = _map_age_to_uci_category(raw_age)
                                all_feature_values.append(age_category)
                            except ValueError:
                                logger.warning(f"Invalid birth date for person {person_id}")
                                all_feature_values.append(0.0)
                        else:
                            all_feature_values.append(0.0)
                    else:
                        all_feature_values.append(0.0)
                    continue
                
                concept_id = feature_info.get(f"{domain_key}_concept_id")
                retrieved_value = 0.0
                if domain_key == "measurement":
                    measurements = db.get_patient_measurements(
                        person_id, 
                        [concept_id] if concept_id else None,
                        limit=1
                    )
                    if measurements and measurements[0].get("value_as_number") is not None:
                        retrieved_value = float(measurements[0]["value_as_number"])
                
                elif domain_key == "observation":
                    observations = db.get_patient_observations(
                        person_id,
                        [concept_id] if concept_id else None,
                        limit=1
                    )
                    if observations:
                        if observations[0].get("value_as_number") is not None:
                            retrieved_value = float(observations[0]["value_as_number"])
                        else:
                            retrieved_value = 1.0  # Present

                elif domain_key == "condition":
                    conditions = db.get_patient_conditions(
                        person_id,
                        [concept_id] if concept_id else None,
                        limit=1
                    )
                    retrieved_value = 1.0 if conditions else 0.0
                
                all_feature_values.append(retrieved_value)
        
        if not all_feature_values:
            return _generate_mock_data(schema, person_id)
        
        return np.array([all_feature_values])
        
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        return _generate_mock_data(schema, person_id)

def get_data(schema: Dict, person_id: Optional[int] = None) -> np.array:
    """
    BACKWARD COMPATIBLE function that maintains exact same interface.
    Your existing code will work unchanged.
    """
    if person_id is None:
        logger.warning("No person_id provided to get_data")
        return _generate_mock_data(schema, person_id) 
    
    return extract_patient_data(schema, person_id) 

# Additional utility functions for data loading and transformation
def load_custom_concepts_from_definitions():
    """Load custom concepts from ALL_DEFINITIONS."""
    if not ALL_DEFINITIONS:
        logger.warning("No ALL_DEFINITIONS available")
        return
    
    concepts_to_add = []
    today_date = datetime.now().date()
    
    for value_name, definition in ALL_DEFINITIONS.items():
        concept_id = definition.get("omop_concept_id")
        source_value = definition.get("source_value")
        domain_id = definition.get("domain")
        
        if not all([concept_id, source_value, domain_id]):
            logger.warning(f"Incomplete definition for '{value_name}'. Skipping.")
            continue
        
        # Check if concept already exists
        existing_concept = db.get_concept_by_id(concept_id)
        if existing_concept:
            logger.debug(f"Concept {concept_id} already exists. Skipping.")
            continue
        
        concept_data = {
            "concept_id": concept_id,
            "concept_name": source_value.replace('_', ' ').title(),
            "domain_id": domain_id.title(),
            "vocabulary_id": "Local",
            "concept_class_id": "Clinical Finding",
            "standard_concept": "S",
            "concept_code": source_value,
            "valid_start_date": today_date,
            "valid_end_date": datetime(2099, 12, 31).date(),
            "invalid_reason": None
        }
        concepts_to_add.append(concept_data)
    
    if concepts_to_add:
        db.bulk_insert_concepts(concepts_to_add)
        logger.info(f"Added {len(concepts_to_add)} custom concepts")
    else:
        logger.info("All custom concepts already exist")

# Keep existing FHIR transformation functions for compatibility
def transform_fhir_bundle_to_omop(bundle):
    """Placeholder for FHIR transformation - implement as needed."""
    logger.info("transform_fhir_bundle_to_omop called")
    return {}

def _get_omop_standard_concept(fhir_system: str, fhir_code: str, session):
    """Placeholder for concept mapping - implement as needed."""
    logger.info("_get_omop_standard_concept called")
    return {"standard_concept_id": 0, "source_concept_id": 0, "source_value": fhir_code}

def map_gender_to_concept_id(gender_string: Optional[str]) -> int:
    """Maps a gender string to OMOP gender_concept_id."""
    if gender_string:
        gender_lower = gender_string.lower()
        if gender_lower == 'female':
            return 8532  # FEMALE
        elif gender_lower == 'male':
            return 8507  # MALE
    return 0  # Unknown or Not Specified

def map_concept_id_to_gender_string(gender_concept_id: Optional[int]) -> str:
    """Maps an OMOP gender_concept_id to a display string."""
    if gender_concept_id == 8532:
        return "Female"
    elif gender_concept_id == 8507:
        return "Male"
    return "N/A"

def parse_date_to_omop_components(date_input: Optional[Any]) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Parses a date input (string, date, datetime) into OMOP year, month, day.
    Returns (None, None, None) if parsing fails or input is None.
    """
    if not date_input:
        return None, None, None

    parsed_date: Optional[date] = None
    if isinstance(date_input, str):
        try:
            # Attempt to parse common ISO format and other potential formats if needed
            parsed_date = datetime.strptime(date_input, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Could not parse date string: {date_input}")
            return None, None, None
    elif isinstance(date_input, datetime):
        parsed_date = date_input.date()
    elif isinstance(date_input, date):
        parsed_date = date_input
    else:
        logger.warning(f"Unsupported date type for OMOP components: {type(date_input)}")
        return None, None, None

    if parsed_date:
        return parsed_date.year, parsed_date.month, parsed_date.day
    return None, None, None

def format_omop_person_for_display(person_record: omop54.Person) -> Dict[str, str]:
    """Formats an OMOP Person record for display."""
    if not person_record:
        return {"name": "N/A", "dob_display": "N/A", "gender_display": "N/A"}

    name = person_record.person_source_value or "N/A"
    
    dob_display = "N/A"
    if person_record.year_of_birth and person_record.month_of_birth and person_record.day_of_birth:
        try:
            dob_date = date(person_record.year_of_birth, person_record.month_of_birth, person_record.day_of_birth)
            dob_display = dob_date.strftime("%B %d, %Y") # e.g., May 15, 1985
        except ValueError:
            dob_display = "Invalid Date" # Should not happen if data is clean
            
    gender_display = map_concept_id_to_gender_string(person_record.gender_concept_id)
    
    return {
        "name": name,
        "dob_display": dob_display,
        "gender_display": gender_display
    }

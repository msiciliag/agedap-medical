"""
FHIR Bundle to OMOP CDM data mapping and storage.
Handles conversion from FHIR resources to OMOP CDM format.
"""
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sys

from utils.fhir import fhir_data_manager
from utils.db import DatabaseManager
from omopmodel import OMOP_5_4_declarative as omop54

# Add project root to path for standard_definitions
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from standard_definitions.terminology_definitions import ALL_DEFINITIONS
except ImportError:
    ALL_DEFINITIONS = {}
    logging.warning("Could not import ALL_DEFINITIONS")

logger = logging.getLogger(__name__)

class FHIRToOMOPMapper:
    """Maps FHIR Bundle data to OMOP CDM format and stores it."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.concept_mapping = self._build_concept_mapping()
    
    def _build_concept_mapping(self) -> Dict[str, Dict]:
        """Build mapping from FHIR codes to OMOP concept IDs."""
        mapping = {}
        
        for value_name, definition in ALL_DEFINITIONS.items():
            source_value = definition.get('source_value')
            omop_concept_id = definition.get('omop_concept_id')
            domain = definition.get('domain')
            
            if source_value and omop_concept_id:
                mapping[source_value] = {
                    'omop_concept_id': omop_concept_id,
                    'domain': domain,
                    'value_name': value_name
                }
        
        logger.info(f"Built concept mapping with {len(mapping)} entries")
        return mapping
    
    def process_patient_bundles(
        self,
        patient_id: str,
        service_names: List[str],
        overwrite_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Process all bundles for a patient and store in OMOP CDM.
        
        Args:
            patient_id: Patient identifier
            service_names: List of service names to process
            overwrite_existing: Whether to overwrite existing data
            
        Returns:
            Processing result dictionary
        """
        result = {
            'patient_id': patient_id,
            'success': False,
            'person_created': False,
            'measurements_created': 0,
            'observations_created': 0,
            'conditions_created': 0,
            'errors': []
        }
        
        try:
            # Check if person already exists
            person_id = int(patient_id)
            person_exists = DatabaseManager.person_exists(person_id)
            
            if person_exists and not overwrite_existing:
                logger.info(f"Person {person_id} already exists, skipping unless overwrite_existing=True")
                result['success'] = True
                return result
            
            # Process each service bundle
            all_bundle_data = {}
            demographics_data = None
            
            for service_name in service_names:
                bundle_data = fhir_data_manager.load_service_bundle(patient_id, service_name)
                if bundle_data:
                    all_bundle_data[service_name] = bundle_data
                    
                    # Extract demographics from first available bundle
                    if not demographics_data and bundle_data.get('patient_data'):
                        demographics_data = bundle_data['patient_data']
                        logger.info(f"Found demographics in {service_name} bundle")
                else:
                    error_msg = f"No bundle data found for service {service_name}"
                    result['errors'].append(error_msg)
                    logger.warning(error_msg)
            
            if not all_bundle_data:
                error_msg = "No bundle data found for any service"
                result['errors'].append(error_msg)
                logger.error(error_msg)
                return result
            
            # Create or update person record
            if not person_exists or overwrite_existing:
                person_result = self._create_person_record(person_id, demographics_data)
                if person_result['success']:
                    result['person_created'] = True
                    logger.info(f"Person {person_id} created successfully")
                else:
                    result['errors'].extend(person_result['errors'])
                    logger.error(f"Failed to create person {person_id}")
                    return result
            
            # Process clinical data from all bundles
            for service_name, bundle_data in all_bundle_data.items():
                clinical_result = self._process_clinical_data(person_id, service_name, bundle_data)
                
                result['measurements_created'] += clinical_result['measurements_created']
                result['observations_created'] += clinical_result['observations_created']
                result['conditions_created'] += clinical_result['conditions_created']
                result['errors'].extend(clinical_result['errors'])
                
                logger.info(f"Processed {service_name}: {clinical_result['measurements_created']} measurements, "
                           f"{clinical_result['observations_created']} observations, "
                           f"{clinical_result['conditions_created']} conditions")
            
            result['success'] = True
            logger.info(f"Successfully processed all bundles for patient {patient_id}")
            
        except Exception as e:
            error_msg = f"Error processing patient bundles: {e}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def _create_person_record(self, person_id: int, demographics_data: Optional[Dict]) -> Dict[str, Any]:
        """Create OMOP Person record from FHIR demographics."""
        result = {
            'success': False,
            'errors': []
        }
        
        try:
            # Default person data
            person_data = {
                'person_id': person_id,
                'gender_concept_id': 0,  # Unknown
                'year_of_birth': None,
                'month_of_birth': None,
                'day_of_birth': None,
                'birth_datetime': None,
                'race_concept_id': 0,  # Unknown
                'ethnicity_concept_id': 0,  # Unknown
                'person_source_value': f"FHIR_Patient_{person_id}",
                'gender_source_value': None
            }
            
            # Extract demographics if available
            if demographics_data:
                # Extract gender
                gender = demographics_data.get('gender', '').lower()
                if gender == 'female':
                    person_data['gender_concept_id'] = 8532  # FEMALE
                    person_data['gender_source_value'] = 'female'
                elif gender == 'male':
                    person_data['gender_concept_id'] = 8507  # MALE
                    person_data['gender_source_value'] = 'male'
                
                # Extract birth date
                birth_date = demographics_data.get('date_of_birth')
                if birth_date:
                    if isinstance(birth_date, str):
                        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                    elif isinstance(birth_date, datetime):
                        birth_date = birth_date.date()
                    
                    if birth_date:
                        person_data['year_of_birth'] = birth_date.year
                        person_data['month_of_birth'] = birth_date.month
                        person_data['day_of_birth'] = birth_date.day
                        person_data['birth_datetime'] = datetime.combine(birth_date, datetime.min.time())
                
                # Extract name for source value
                name = demographics_data.get('name')
                if name:
                    person_data['person_source_value'] = f"FHIR_{name.replace(' ', '_')}"
            
            # Create or update person record
            if DatabaseManager.person_exists(person_id):
                logger.info(f"Person {person_id} already exists, skipping creation")
            else:
                created_id = DatabaseManager.create_person(person_data)
                if created_id == person_id:
                    logger.info(f"Created person record for ID {person_id}")
                else:
                    raise Exception(f"Person creation returned unexpected ID: {created_id}")
            
            result['success'] = True
            
        except Exception as e:
            error_msg = f"Error creating person record: {e}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def _process_clinical_data(self, person_id: int, service_name: str, bundle_data: Dict) -> Dict[str, Any]:
        """Process clinical data from a bundle."""
        result = {
            'measurements_created': 0,
            'observations_created': 0,
            'conditions_created': 0,
            'errors': []
        }
        
        try:
            observations = bundle_data.get('observations', [])
            current_date = date.today()
            current_datetime = datetime.now()
            
            measurements_to_create = []
            observations_to_create = []
            conditions_to_create = []
            
            for obs_data in observations:
                try:
                    # Map FHIR observation to OMOP
                    omop_data = self._map_observation_to_omop(obs_data, person_id, current_date, current_datetime)
                    
                    if omop_data:
                        domain = omop_data.get('domain', 'Observation')
                        
                        if domain == 'Measurement':
                            measurements_to_create.append(omop_data['data'])
                        elif domain == 'Condition':
                            conditions_to_create.append(omop_data['data'])
                        else:  # Default to Observation
                            observations_to_create.append(omop_data['data'])
                
                except Exception as e:
                    error_msg = f"Error processing observation: {e}"
                    result['errors'].append(error_msg)
                    logger.warning(error_msg)
            
            # Bulk insert data
            if measurements_to_create:
                DatabaseManager.bulk_insert_measurements(measurements_to_create)
                result['measurements_created'] = len(measurements_to_create)
            
            if observations_to_create:
                DatabaseManager.bulk_insert_observations(observations_to_create)
                result['observations_created'] = len(observations_to_create)
            
            if conditions_to_create:
                DatabaseManager.bulk_insert_conditions(conditions_to_create)
                result['conditions_created'] = len(conditions_to_create)
            
        except Exception as e:
            error_msg = f"Error processing clinical data: {e}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def _map_observation_to_omop(
        self, 
        obs_data: Dict, 
        person_id: int, 
        record_date: date, 
        record_datetime: datetime
    ) -> Optional[Dict]:
        """Map a FHIR observation to OMOP format."""
        try:
            # Extract key identifiers
            code = obs_data.get('code')
            display = obs_data.get('display', '')
            value = obs_data.get('value')
            
            # Try to find matching concept mapping
            concept_mapping = None
            omop_concept_id = None
            
            # Look for mapping by code or display
            for source_value, mapping in self.concept_mapping.items():
                if (code and source_value == code) or (display and source_value.lower() in display.lower()):
                    concept_mapping = mapping
                    omop_concept_id = mapping['omop_concept_id']
                    break
            
            # If no mapping found, try to infer from display text
            if not concept_mapping and display:
                for source_value, mapping in self.concept_mapping.items():
                    if any(word in display.lower() for word in source_value.lower().split('_')):
                        concept_mapping = mapping
                        omop_concept_id = mapping['omop_concept_id']
                        break
            
            # Skip if no mapping found
            if not concept_mapping:
                logger.debug(f"No mapping found for observation: {code} - {display}")
                return None
            
            domain = concept_mapping.get('domain', 'Observation')
            
            # Convert value to appropriate format
            numeric_value = None
            string_value = None
            
            if isinstance(value, (int, float)):
                numeric_value = float(value)
            elif isinstance(value, bool):
                numeric_value = 1.0 if value else 0.0
            elif isinstance(value, str):
                try:
                    numeric_value = float(value)
                except ValueError:
                    string_value = value
                    # Try to convert common string values
                    if value.lower() in ['yes', 'true', 'positive', '1']:
                        numeric_value = 1.0
                    elif value.lower() in ['no', 'false', 'negative', '0']:
                        numeric_value = 0.0
            
            # Create appropriate OMOP record
            if domain == 'Measurement':
                return {
                    'domain': 'Measurement',
                    'data': {
                        'person_id': person_id,
                        'measurement_concept_id': omop_concept_id,
                        'measurement_date': record_date,
                        'measurement_datetime': record_datetime,
                        'measurement_type_concept_id': 32817,  # Lab result
                        'value_as_number': numeric_value,
                        'value_as_concept_id': None,
                        'unit_concept_id': None,
                        'range_low': None,
                        'range_high': None,
                        'measurement_source_value': code or display,
                        'measurement_source_concept_id': omop_concept_id,
                        'unit_source_value': obs_data.get('unit'),
                        'value_source_value': str(value) if value is not None else None
                    }
                }
            
            elif domain == 'Condition':
                return {
                    'domain': 'Condition',
                    'data': {
                        'person_id': person_id,
                        'condition_concept_id': omop_concept_id,
                        'condition_start_date': record_date,
                        'condition_start_datetime': record_datetime,
                        'condition_end_date': None,
                        'condition_end_datetime': None,
                        'condition_type_concept_id': 32020,  # EHR record
                        'condition_status_concept_id': None,
                        'stop_reason': None,
                        'condition_source_value': code or display,
                        'condition_source_concept_id': omop_concept_id,
                        'condition_status_source_value': None
                    }
                }
            
            else:  # Default to Observation
                return {
                    'domain': 'Observation',
                    'data': {
                        'person_id': person_id,
                        'observation_concept_id': omop_concept_id,
                        'observation_date': record_date,
                        'observation_datetime': record_datetime,
                        'observation_type_concept_id': 38000280,  # Observation from EHR
                        'value_as_number': numeric_value,
                        'value_as_string': string_value,
                        'value_as_concept_id': None,
                        'qualifier_concept_id': None,
                        'unit_concept_id': None,
                        'observation_source_value': code or display,
                        'observation_source_concept_id': omop_concept_id,
                        'unit_source_value': obs_data.get('unit'),
                        'qualifier_source_value': None
                    }
                }
            
        except Exception as e:
            logger.error(f"Error mapping observation to OMOP: {e}")
            return None

# Global mapper instance
fhir_to_omop_mapper = FHIRToOMOPMapper()

# Convenience function
def map_patient_from_fhir_sources(
    patient_id: str,
    hapi_base_url: str = None,
    service_names: List[str] = None,
    overwrite_existing: bool = False
) -> Dict[str, Any]:
    """
    Map patient data from FHIR sources to OMOP CDM.
    
    Args:
        patient_id: Patient identifier
        hapi_base_url: HAPI FHIR server URL (optional)
        service_names: List of service names to process
        overwrite_existing: Whether to overwrite existing data
        
    Returns:
        Processing result dictionary
    """
    return fhir_to_omop_mapper.process_patient_bundles(
        patient_id=patient_id,
        service_names=service_names or ['breast_cancer', 'diabetes'],
        overwrite_existing=overwrite_existing
    )
import logging
from pathlib import Path
import sys
import logging
import datetime
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from standard_definitions.terminology_definitions import ALL_DEFINITIONS


logger = logging.getLogger(__name__)

def transform_patient(fhir_patient_dict, person_id):
    """
    Maps a FHIR patient dict to OMOP CDM person fields.
    Fills in required OMOP fields with defaults if missing.
    """
    gender_str = fhir_patient_dict.get("gender", "").lower()
    if gender_str == "female":
        gender_concept_id = 8532
    elif gender_str == "male":
        gender_concept_id = 8507
    else:
        gender_concept_id = 0

    dob = fhir_patient_dict.get("date_of_birth")
    if hasattr(dob, "year"):
        year_of_birth = dob.year
        month_of_birth = dob.month
        day_of_birth = dob.day
    elif isinstance(dob, str) and dob:
        parts = dob.split("-")
        year_of_birth = int(parts[0])
        month_of_birth = int(parts[1]) if len(parts) > 1 else None
        day_of_birth = int(parts[2]) if len(parts) > 2 else None
    else:
        year_of_birth = month_of_birth = day_of_birth = None

    return {
        "person_id": person_id,
        "gender_concept_id": gender_concept_id,
        "gender_source_value": gender_str,
        "year_of_birth": year_of_birth,
        "month_of_birth": month_of_birth,
        "day_of_birth": day_of_birth,
        "race_concept_id": 0,         
        "ethnicity_concept_id": 0,    
    }

def transform_bundle_to_omop(bundle, patient_id):
    """
    Transforms a FHIR Bundle into a list of OMOP resources.
    
    Args:
        bundle: FHIR Bundle object
        patient_id: Patient identifier
    
    Returns:
        List of OMOP resources
    """
    omop_resources = []
    
    for entry in bundle.entry or []:
        if not hasattr(entry, "resource") or entry.resource is None:
            print("Skipping entry with no resource")
            continue
        resource = entry.resource
        if resource is None:
            logger.warning("Entry resource is None, skipping.")
            continue
        print(f"Processing resource: {resource.id}")
        print(resource.code.coding[0].code if hasattr(resource, "code") and resource.code else "No code available")
        definition = get_definition_by_source_value(resource.code.coding[0].code) if hasattr(resource, "code") and resource.code else None
        resource_type = definition.get("domain") if definition else None
        print(f"Processing resource of type: {resource_type}")

        if resource_type == 'Observation':
            omop_resource = map_observation_to_omop(resource, patient_id)
            if omop_resource:
                omop_resources.append(omop_resource)

        elif resource_type == 'Condition':
            omop_resource = map_condition_to_omop(resource, patient_id)
            if omop_resource:
                omop_resources.append(omop_resource)          

        elif resource_type == 'Measurement':
            omop_resource = map_measurement_to_omop(resource, patient_id)
            if omop_resource:
                omop_resources.append(omop_resource)

    return omop_resources

def get_definition_by_source_value(source_value):
    for key, definition in ALL_DEFINITIONS.items():
        if definition.get("source_value") == source_value:
            return definition
    return None

def map_observation_to_omop(observation, patient_id):
    """
    Maps a FHIR Observation resource to an OMOP Observation, uses the definitions from ALL_DEFINITIONS.
    
    Args:
        observation: FHIR Observation resource
        patient_id: Patient identifier
    
    Returns:
        OMOP Observation resource or None if mapping fails
    """
    try:
        code = observation.code.coding[0].code
        definition = get_definition_by_source_value(code)
        if not definition:
            logger.error(f"No definition found for observation code: {code}")
            return None
        obs_date = getattr(observation, "effectiveDateTime", None)
        if obs_date is None:
            obs_date = datetime.now().date()
        omop_observation = {
            "__resource_type__": "Observation",
            "observation_id": None,
            "person_id": patient_id,
            "observation_concept_id": definition["omop_concept_id"],
            "observation_date": observation.effectiveDateTime.date() if hasattr(observation.effectiveDateTime, "date") else observation.effectiveDateTime,
            "observation_type_concept_id": 32865,
            "value_as_number": observation.valueQuantity.value if observation.valueQuantity else None,
            "value_as_string": observation.valueString if observation.valueString else None,
            "unit_concept_id": definition.get("unit_concept_id", 0),
            "observation_source_value": observation.code.coding[0].code,
        }
        
        return omop_observation
    except Exception as e:
        logger.error(f"Error mapping Observation to OMOP: {e}")
        return None
    
def map_condition_to_omop(condition, patient_id):
    """
    Maps a FHIR Condition resource to an OMOP Condition, uses the definitions from ALL_DEFINITIONS.
    
    Args:
        condition: FHIR Condition resource
        patient_id: Patient identifier
    
    Returns:
        OMOP Condition resource or None if mapping fails
    """
    try:
        code = condition.code.coding[0].code
        definition = get_definition_by_source_value(code)
        if not definition:
            logger.error(f"No definition found for condition code: {condition.code.coding[0].code}")
            return None
        omop_condition = {
            "__resource_type__": "Condition",
            "condition_id": None,
            "person_id": patient_id,
            "condition_concept_id": definition["omop_concept_id"],
            "condition_start_date": condition.onsetDateTime,
            "condition_end_date": getattr(condition, "abatementDateTime", None),
            "condition_type_concept_id": 32020,
            "condition_source_value": condition.code.coding[0].code,
        }
        
        return omop_condition
    except Exception as e:
        logger.error(f"Error mapping Condition to OMOP: {e}")
        return None 
    
def map_measurement_to_omop(measurement, patient_id):
    """
    Maps a FHIR Measurement resource to an OMOP Measurement, uses the definitions from ALL_DEFINITIONS.
    
    Args:
        measurement: FHIR Measurement resource
        patient_id: Patient identifier
    
    Returns:
        OMOP Measurement resource or None if mapping fails
    """
    try:
        code = measurement.code.coding[0].code
        definition = get_definition_by_source_value(code)
        if not definition:
            logger.error(f"No definition found for measurement code: {measurement.code.coding[0].code}")
            return None
        
        omop_measurement = {
            "__resource_type__": "Measurement",
            "measurement_id": None,
            "person_id": patient_id,
            "measurement_concept_id": definition["omop_concept_id"],
            "measurement_date": measurement.effectiveDateTime,
            "measurement_type_concept_id": 44818702,
            "value_as_number": measurement.valueQuantity.value if measurement.valueQuantity else None,
            "unit_concept_id": definition.get("unit_concept_id", 0),
            "measurement_source_value": measurement.code.coding[0].code,
        }
        
        return omop_measurement
    except Exception as e:
        logger.error(f"Error mapping Measurement to OMOP: {e}")
        return None
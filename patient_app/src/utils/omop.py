import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from utils.db import DatabaseManager 
from omopmodel import OMOP_5_4_declarative as omop54

def get_data(schema):
    """
    Recupera datos del modelo OMOP-CDM utilizando el esquema proporcionado.
    
    Args:
        schema (dict): Un diccionario que define los campos requeridos en el resultado.
    
    Returns:
        np.array: Matriz NumPy con los datos solicitados.
    """
    print("Recuperando datos de la base de datos OMOP-CDM...")
    print(f"Esquema: {schema}")
    
    try:
        session = DatabaseManager.get_db_session()
        result_data = []
        
        if 'measurement' in schema:
            # Extraer datos basados en las mediciones requeridas
            measurements_list = schema['measurement']
            
            # Crear una lista para almacenar los valores en el orden requerido
            values = []
            
            for measurement_info in measurements_list:
                print(f"Procesando medición: {measurement_info}")
                # Obtener el valor_name (nombre de la columna en el conjunto de resultados)
                value_name = measurement_info.get('value_name')
                
                # Buscar por measurement_concept_id si está disponible y no es 0
                concept_id = measurement_info.get('measurement_concept_id')
                source_value = measurement_info.get('measurement_source_value')
                
                measurement = None
                if concept_id and concept_id != 0:
                    print(f"Buscando medición por concept_id: {concept_id}")
                    # Buscar por ID del concepto (más preciso)
                    measurement = session.query(omop54.Measurement).filter(
                        omop54.Measurement.measurement_concept_id == concept_id
                    ).order_by(omop54.Measurement.measurement_date.desc()).first()
                elif source_value:
                    # Buscar por valor de origen
                    print(f"Buscando medición por source_value: {source_value}")
                    measurement = session.query(omop54.Measurement).filter(
                        omop54.Measurement.measurement_source_value == source_value
                    ).order_by(omop54.Measurement.measurement_date.desc()).first()
                
                # Extraer el valor si se encuentra la medición
                if measurement and measurement.value_as_number is not None:
                    print(f"Medición encontrada: {measurement.value_as_number}")
                    values.append(measurement.value_as_number)
                else:
                    print(f"No se encontró medición para {value_name} (concept_id: {concept_id}, source_value: {source_value})")
                    values.append(0.0)
            
            # Agregar la fila de valores a nuestros resultados
            result_data.append(values)
        
        # Si existen otros tipos de datos en el esquema (como procedure, condition, etc.)
        # podríamos procesarlos de manera similar
        
        # Verificar si tenemos datos
        if not result_data:
            print("No se encontraron datos en OMOP-CDM, utilizando datos simulados de respaldo.")
            return get_mock_data_for_schema(schema)
        
        return np.array(result_data)
    
    except Exception as e:
        print(f"Error al acceder a la base de datos OMOP-CDM: {str(e)}")
        return []

def get_mock_data_for_schema(schema):
    """
    Genera datos simulados basados en el esquema proporcionado.
    
    Args:
        schema (dict or list): Un diccionario que define los campos requeridos (e.g., para 'measurement')
                               o una lista de nombres de características.
    
    Returns:
        np.array: Matriz NumPy 2D con datos simulados (una fila de datos).
    """
    print("Generando datos simulados para el esquema.")
    current_row_values = []

    if isinstance(schema, dict) and 'measurement' in schema:
        measurements_list = schema['measurement']
        for _ in measurements_list:
            # Genera un valor aleatorio entre 0.1 y 10.0
            current_row_values.append(np.random.uniform(0.1, 10.0))
        # current_row_values is populated or [] if measurements_list was empty
    
    elif isinstance(schema, list): # Handles schemas like ['feature1', 'feature2', ...]
        if schema: # If the list of feature names is not empty
            for _ in schema: # For each feature name
                # Mocking with random 0 or 1 for list-based schema features
                current_row_values.append(np.random.randint(0, 2))
        # If schema was an empty list, current_row_values remains []
        
    # else:
        # If schema is neither a dict with 'measurement' nor a list,
        # current_row_values remains []. An empty row will be wrapped into a 2D array.

    # Always return a 2D array by wrapping current_row_values in an outer list.
    # This creates np.array([[val1, val2, ...]]) or np.array([[]]) if current_row_values is empty.
    return np.array([current_row_values])

def transform_fhir_bundle_to_omop(bundle):
    """
    Transforma un FHIR Bundle a un formato compatible con OMOP-CDM.
    
    Args:
        bundle (Bundle): Un objeto Bundle de FHIR.
    
    Returns:
        dict: Un diccionario con los datos transformados, donde las claves son
              nombres de tablas OMOP y los valores son listas de registros.
    """
    omop_data = {
        "PERSON": [],
        "VISIT_OCCURRENCE": [],
        "CONDITION_OCCURRENCE": [],
        "PROCEDURE_OCCURRENCE": [],
        "DRUG_EXPOSURE": [],
        "MEASUREMENT": [],
        "OBSERVATION": [],
        "DEVICE_EXPOSURE": [],
        "LOCATION": [],
        "PROVIDER": []
        # Agrega otras tablas OMOP según sea necesario
    }

    if not bundle or not bundle.entry:
        print("Bundle vacío o sin entradas.")
        return omop_data

    session = DatabaseManager.get_db_session() # Obtain session for vocabulary lookups

    for entry in bundle.entry:
        if not entry.resource:
            continue

        resource = entry.resource
        resource_type = resource.resourceType

        print(f"Procesando recurso FHIR: {resource_type}")

        if resource_type == "Patient":
            person_source_value = getattr(resource, 'id', None)
            
            gender_fhir = getattr(resource, 'gender', None)
            gender_concept_id = 0  # Default to Unknown or Unspecified
            gender_source_value = gender_fhir
            if gender_fhir:
                if gender_fhir.lower() == 'male':
                    gender_concept_id = 8507
                elif gender_fhir.lower() == 'female':
                    gender_concept_id = 8532
                elif gender_fhir.lower() == 'other':
                    gender_concept_id = 0 # Or a specific OMOP concept for 'other' if available
                elif gender_fhir.lower() == 'unknown':
                    gender_concept_id = 0 # OMOP concept for 'unknown'
            
            birth_date_str = getattr(resource, 'birthDate', None)
            year_of_birth = None
            month_of_birth = None
            day_of_birth = None
            birth_datetime_obj = None

            if birth_date_str:
                try:
                    parts = birth_date_str.split('-')
                    year_of_birth = int(parts[0])
                    if len(parts) > 1:
                        month_of_birth = int(parts[1])
                    else: # Year only, default month to 1 for datetime
                        month_of_birth = 1
                    if len(parts) > 2:
                        day_of_birth = int(parts[2])
                    else: # Year-Month or Year only, default day to 1 for datetime
                        day_of_birth = 1
                    
                    # Create datetime object at midnight
                    birth_datetime_obj = datetime(year_of_birth, month_of_birth, day_of_birth)
                    
                    # If original precision was only year or year-month, nullify month/day for those specific fields
                    if len(parts) == 1: # YYYY
                        month_of_birth = None
                        day_of_birth = None
                    elif len(parts) == 2: # YYYY-MM
                        day_of_birth = None

                except ValueError:
                    print(f"Warning: Could not parse birthDate '{birth_date_str}' for Patient {person_source_value}")
            
            # Placeholder for race and ethnicity - requires FHIR extensions typically
            race_concept_id = 0
            ethnicity_concept_id = 0
            race_source_value = None
            ethnicity_source_value = None

            # Placeholder for location_id (from Patient.address) and provider_id (from Patient.generalPractitioner)
            location_id = None
            provider_id = None

            person_record = {
                "person_source_value": person_source_value,
                "gender_concept_id": gender_concept_id,
                "year_of_birth": year_of_birth,
                "month_of_birth": month_of_birth,
                "day_of_birth": day_of_birth,
                "birth_datetime": birth_datetime_obj.isoformat() if birth_datetime_obj else None,
                "race_concept_id": race_concept_id,
                "ethnicity_concept_id": ethnicity_concept_id,
                "location_id": location_id,
                "provider_id": provider_id,
                "gender_source_value": gender_source_value,
                "race_source_value": race_source_value,
                "ethnicity_source_value": ethnicity_source_value,
                # person_id is typically generated by the database upon insertion
            }
            omop_data["PERSON"].append(person_record)

            # TODO: Map Patient.address to LOCATION table
            # TODO: Map Patient.generalPractitioner to PROVIDER table
            # TODO: Map Patient extensions for race and ethnicity if available

        elif resource_type == "Encounter":
            visit_data = {}
            # person_id will need to be linked from Encounter.subject.reference
            # provider_id might be linked from Encounter.participant.individual.reference
            # visit_occurrence_id is typically auto-generated or from a source system

            # Visit Concept ID (from Encounter.class or Encounter.type)
            # Encounter.class is often a good candidate for visit_concept_id
            # Encounter.type can provide more specific details, sometimes mapped to visit_type_concept_id
            # For simplicity, let's try to map Encounter.class to visit_concept_id
            # and one of Encounter.type to visit_type_concept_id.
            
            visit_concept_id = 0 # Default to unknown
            visit_source_value = None
            visit_source_concept_id = 0

            if hasattr(resource, 'class_') and resource.class_ and resource.class_.system and resource.class_.code:
                # Note: fhir.resources uses 'class_' due to 'class' being a Python keyword
                mapping_info = _get_omop_standard_concept(resource.class_.system, resource.class_.code, session)
                visit_concept_id = mapping_info["standard_concept_id"]
                # visit_source_value could be the class code itself, or a display name if preferred
                visit_source_value = resource.class_.code 
                # We might not always have a direct source_concept_id for visit_concept_id if it's derived
                # from a high-level class. For now, let's use the mapping result.
                # visit_source_concept_id = mapping_info["source_concept_id"] # Or handle differently

            # Visit Type Concept ID (often from Encounter.type)
            visit_type_concept_id = 0 # Default (e.g., "Visit derived from EHR encounter record")
                                      # Common default is 32817 (EHR encounter record) or similar based on ETL conventions
            
            if hasattr(resource, 'type') and resource.type:
                for encounter_type_coding in resource.type: # resource.type is a list of CodeableConcept
                    if hasattr(encounter_type_coding, 'coding') and encounter_type_coding.coding:
                        # Try to map the first coding found in Encounter.type
                        # A more robust solution might prioritize or select specific systems
                        first_coding = encounter_type_coding.coding[0]
                        if first_coding.system and first_coding.code:
                            type_mapping_info = _get_omop_standard_concept(first_coding.system, first_coding.code, session)
                            # This mapped concept might be used for visit_type_concept_id
                            # or sometimes even to refine visit_concept_id if Encounter.class is too general.
                            # For now, let's assign to visit_type_concept_id
                            visit_type_concept_id = type_mapping_info["standard_concept_id"]
                            # If visit_concept_id was not set by Encounter.class, Encounter.type could be an alternative
                            if visit_concept_id == 0 and visit_source_value is None:
                                visit_concept_id = type_mapping_info["standard_concept_id"]
                                visit_source_value = type_mapping_info["source_value"]
                                visit_source_concept_id = type_mapping_info["source_concept_id"]
                            break # Use the first type found

            # Dates (Encounter.period)
            visit_start_date = None
            visit_start_datetime = None
            visit_end_date = None
            visit_end_datetime = None

            if hasattr(resource, 'period') and resource.period:
                if hasattr(resource.period, 'start') and resource.period.start:
                    try:
                        start_dt_obj = datetime.fromisoformat(resource.period.start.replace("Z", "+00:00"))
                        visit_start_date = start_dt_obj.date()
                        visit_start_datetime = start_dt_obj
                    except ValueError:
                        print(f"Warning: Could not parse Encounter period.start \'{resource.period.start}\'")
                
                if hasattr(resource.period, 'end') and resource.period.end:
                    try:
                        end_dt_obj = datetime.fromisoformat(resource.period.end.replace("Z", "+00:00"))
                        visit_end_date = end_dt_obj.date()
                        visit_end_datetime = end_dt_obj
                    except ValueError:
                        print(f"Warning: Could not parse Encounter period.end \'{resource.period.end}\'")
            
            # If only start_date is available, end_date is often set to start_date in OMOP
            if visit_start_date and not visit_end_date:
                visit_end_date = visit_start_date
                visit_end_datetime = visit_start_datetime


            # Admitting Source Concept ID (from Encounter.hospitalization.admitSource)
            admitting_source_concept_id = 0
            admitting_source_value = None
            if hasattr(resource, 'hospitalization') and resource.hospitalization and \
               hasattr(resource.hospitalization, 'admitSource') and resource.hospitalization.admitSource and \
               hasattr(resource.hospitalization.admitSource, 'coding') and resource.hospitalization.admitSource.coding:
                admit_source_coding = resource.hospitalization.admitSource.coding[0]
                if admit_source_coding.system and admit_source_coding.code:
                    admit_mapping = _get_omop_standard_concept(admit_source_coding.system, admit_source_coding.code, session)
                    admitting_source_concept_id = admit_mapping["standard_concept_id"]
                    admitting_source_value = admit_mapping["source_value"]
            
            # Discharge To Concept ID (from Encounter.hospitalization.dischargeDisposition)
            discharge_to_concept_id = 0
            discharge_to_source_value = None
            if hasattr(resource, 'hospitalization') and resource.hospitalization and \
               hasattr(resource.hospitalization, 'dischargeDisposition') and resource.hospitalization.dischargeDisposition and \
               hasattr(resource.hospitalization.dischargeDisposition, 'coding') and resource.hospitalization.dischargeDisposition.coding:
                discharge_coding = resource.hospitalization.dischargeDisposition.coding[0]
                if discharge_coding.system and discharge_coding.code:
                    discharge_mapping = _get_omop_standard_concept(discharge_coding.system, discharge_coding.code, session)
                    discharge_to_concept_id = discharge_mapping["standard_concept_id"]
                    discharge_to_source_value = discharge_mapping["source_value"]

            # TODO: Link person_id from Encounter.subject.reference
            # TODO: Link provider_id from Encounter.participant.individual.reference
            # TODO: Link preceding_visit_occurrence_id from Encounter.partOf.reference

            visit_occurrence_record = {
                # "person_id": linked_person_id, # Needs to be resolved
                "visit_concept_id": visit_concept_id,
                "visit_start_date": visit_start_date,
                "visit_start_datetime": visit_start_datetime,
                "visit_end_date": visit_end_date,
                "visit_end_datetime": visit_end_datetime,
                "visit_type_concept_id": visit_type_concept_id, # Default or mapped from Encounter.type
                # "provider_id": linked_provider_id, # Needs to be resolved
                # "care_site_id": None, # From Encounter.serviceProvider or Encounter.location
                # "visit_source_value": visit_source_value, # e.g., from Encounter.class.code or Encounter.type text
                "visit_source_concept_id": visit_source_concept_id, # Mapped from source system code for visit
                "admitting_source_concept_id": admitting_source_concept_id,
                "admitting_source_value": admitting_source_value,
                "discharge_to_concept_id": discharge_to_concept_id,
                "discharge_to_source_value": discharge_to_source_value,
                # "preceding_visit_occurrence_id": linked_preceding_visit_id # Needs to be resolved
            }
            omop_data["VISIT_OCCURRENCE"].append(visit_occurrence_record)

        elif resource_type == "Condition":
            condition_data = {}
            
            # Get person_id - this assumes Patient resource is processed first and person_id is available
            # For simplicity, we'll need a way to link this condition to the correct person.
            # This often involves looking up the patient_id based on a reference in the Condition resource.
            # For now, let's assume we can get a person_identifier (e.g. the patient's source_value)
            # and would later link it or that the bundle is for a single patient.
            # A robust solution would involve resolving FHIR references (e.g., Condition.subject.reference)
            
            # patient_id = get_person_id_from_fhir_reference(resource.subject.reference, omop_data["PERSON"]) # Conceptual
            # For ahora, asegúrate de que todos los campos básicos estén presentes, incluso si son None o valores predeterminados
            condition_record = {
                "condition_concept_id": 0,
                "condition_start_date": None,
                "condition_start_datetime": None,
                "condition_end_date": None, # Not mapped yet
                "condition_end_datetime": None, # Not mapped yet
                "condition_type_concept_id": 0, # e.g., from Encounter diagnosis, or EHR problem list item
                "condition_status_concept_id": 0,
                "stop_reason": None, # Not directly from Condition, might be inferred
                "provider_id": None, # From Condition.asserter or Encounter
                "visit_occurrence_id": None, # From Condition.encounter or linked Encounter
                "visit_detail_id": None,
                "condition_source_value": None,
                "condition_source_concept_id": 0,
                "condition_status_source_value": None,
            }

            if hasattr(resource, 'code') and resource.code and hasattr(resource.code, 'coding') and resource.code.coding:
                # Prioritize SNOMED, then other codings
                # This is a simple prioritization, could be more complex
                coding_to_use = None
                for c in resource.code.coding:
                    if c.system == "http://snomed.info/sct":
                        coding_to_use = c
                        break
                if not coding_to_use and resource.code.coding:
                    coding_to_use = resource.code.coding[0]

                if coding_to_use and coding_to_use.system and coding_to_use.code:
                    mapping_info = _get_omop_standard_concept(coding_to_use.system, coding_to_use.code, session)
                    condition_record['condition_concept_id'] = mapping_info["standard_concept_id"]
                    condition_record['condition_source_value'] = mapping_info["source_value"]
                    condition_record['condition_source_concept_id'] = mapping_info["source_concept_id"]
            else: # No code provided
                condition_record['condition_concept_id'] = 0 # Unknown concept
                condition_record['condition_source_value'] = None
                condition_record['condition_source_concept_id'] = 0

            # Dates
            # Condition.onsetDateTime, Condition.onsetAge, Condition.onsetPeriod, Condition.onsetString, Condition.onsetRange
            # OMOP: condition_start_date, condition_start_datetime, condition_end_date, condition_end_datetime
            # For simplicity, let's try to get onsetDateTime
            if hasattr(resource, 'onsetDateTime') and resource.onsetDateTime:
                try:
                    onset_datetime = datetime.fromisoformat(resource.onsetDateTime.replace("Z", "+00:00"))
                    condition_record['condition_start_date'] = onset_datetime.date()
                    condition_record['condition_start_datetime'] = onset_datetime
                except ValueError:
                    print(f"Warning: Could not parse onsetDateTime \'{resource.onsetDateTime}\' for Condition")
                    condition_record['condition_start_date'] = None # Or a default date
                    condition_record['condition_start_datetime'] = None
            else: # If no onsetDateTime, set to a default or handle based on other onset[x] types
                condition_record['condition_start_date'] = None # Placeholder
                condition_record['condition_start_datetime'] = None


            # Condition.recordedDate (when condition was recorded)
            if hasattr(resource, 'recordedDate') and resource.recordedDate:
                 try:
                    recorded_datetime = datetime.fromisoformat(resource.recordedDate.replace("Z", "+00:00"))
                    # This might map to an observation or metadata field in some ETLs,
                    # but OMOP condition_occurrence doesn't have a direct 'recorded_date'
                    # It's more about the event's date (start/end)
                 except ValueError:
                    print(f"Warning: Could not parse recordedDate \'{resource.recordedDate}\'")


            # Condition Status (clinicalStatus and verificationStatus)
            # OMOP condition_status_concept_id, condition_status_source_value
            # This requires mapping FHIR statuses to OMOP concept IDs for condition status
            # Example: 'active' from clinicalStatus might map to an OMOP concept.
            # For ahora, asegúrate de que todos los campos básicos estén presentes, incluso si son None o valores predeterminados
            condition_record['condition_status_concept_id'] = 0 
            condition_record['condition_status_source_value'] = None
            if hasattr(resource, 'clinicalStatus') and resource.clinicalStatus and hasattr(resource.clinicalStatus, 'coding') and resource.clinicalStatus.coding:
                # Typically, clinicalStatus is a codeableConcept. We'd map its code.
                # E.g., http://terminology.hl7.org/CodeSystem/condition-clinical active, relapse, remission, resolved
                condition_record['condition_status_source_value'] = resource.clinicalStatus.coding[0].code # Take the first one's code as source
                # TODO: Map this source_value to a standard OMOP condition_status_concept_id

            # For ahora, asegúrate de que todos los campos básicos estén presentes, incluso si son None o valores predeterminados
            condition_record = {
                "condition_concept_id": condition_record.get('condition_concept_id', 0),
                "condition_start_date": condition_record.get('condition_start_date'),
                "condition_start_datetime": condition_record.get('condition_start_datetime'),
                "condition_end_date": condition_record.get('condition_end_date'), # Not mapped yet
                "condition_end_datetime": condition_record.get('condition_end_datetime'), # Not mapped yet
                "condition_type_concept_id": 0, # e.g., from Encounter diagnosis, or EHR problem list item
                "condition_status_concept_id": condition_record.get('condition_status_concept_id', 0),
                "stop_reason": None, # Not directly from Condition, might be inferred
                "provider_id": None, # From Condition.asserter or Encounter
                "visit_occurrence_id": None, # From Condition.encounter or linked Encounter
                "visit_detail_id": None,
                "condition_source_value": condition_record.get('condition_source_value'),
                "condition_source_concept_id": condition_record.get('condition_source_concept_id', 0),
                "condition_status_source_value": condition_record.get('condition_status_source_value'),
                # person_id needs to be linked
            }
            # Add person_id if available (e.g. if processing a single patient bundle or resolved reference)
            # condition_record['person_id'] = patient_id 
            
            omop_data["CONDITION_OCCURRENCE"].append(condition_record)

        elif resource_type == "Procedure":
            procedure_data = {}
            # TODO: Link person_id from Procedure.subject.reference
            # TODO: Link visit_occurrence_id from Procedure.encounter.reference
            # TODO: Link provider_id from Procedure.performer.actor.reference

            # Procedure Code (Procedure.code)
            procedure_concept_id = 0
            procedure_source_value = None
            procedure_source_concept_id = 0
            if hasattr(resource, 'code') and resource.code and hasattr(resource.code, 'coding') and resource.code.coding:
                # Simple prioritization: SNOMED, then first available
                coding_to_use = None
                for c in resource.code.coding:
                    if c.system == "http://snomed.info/sct": # Or other primary systems like CPT4, ICD-P
                        coding_to_use = c
                        break
                if not coding_to_use and resource.code.coding:
                    coding_to_use = resource.code.coding[0]
                
                if coding_to_use and coding_to_use.system and coding_to_use.code:
                    mapping_info = _get_omop_standard_concept(coding_to_use.system, coding_to_use.code, session)
                    procedure_concept_id = mapping_info["standard_concept_id"]
                    procedure_source_value = mapping_info["source_value"]
                    procedure_source_concept_id = mapping_info["source_concept_id"]

            # Procedure Date/DateTime (Procedure.performedDateTime or Procedure.performedPeriod)
            procedure_date = None
            procedure_datetime = None
            if hasattr(resource, 'performedDateTime') and resource.performedDateTime:
                try:
                    dt_obj = datetime.fromisoformat(resource.performedDateTime.replace("Z", "+00:00"))
                    procedure_date = dt_obj.date()
                    procedure_datetime = dt_obj
                except ValueError:
                    print(f"Warning: Could not parse Procedure performedDateTime '{resource.performedDateTime}'")
            elif hasattr(resource, 'performedPeriod') and resource.performedPeriod and hasattr(resource.performedPeriod, 'start') and resource.performedPeriod.start:
                try: # Use start of the period
                    dt_obj = datetime.fromisoformat(resource.performedPeriod.start.replace("Z", "+00:00"))
                    procedure_date = dt_obj.date()
                    procedure_datetime = dt_obj
                except ValueError:
                    print(f"Warning: Could not parse Procedure performedPeriod.start '{resource.performedPeriod.start}'")
            
            # Procedure Type Concept ID (e.g. from claim, EHR order) - often a default or from context
            procedure_type_concept_id = 0 # Default (e.g., 38000275 - EHR order entry)

            # Modifier Concept ID (Procedure.modifier) - if applicable
            modifier_concept_id = 0 
            # modifier_source_value = None # If modifiers are present, map them

            # Quantity (Procedure.extension with a specific URL for quantity, or derived)
            quantity = None # Typically 1 for procedures unless specified

            procedure_record = {
                # "person_id": linked_person_id,
                "procedure_concept_id": procedure_concept_id,
                "procedure_date": procedure_date,
                "procedure_datetime": procedure_datetime,
                "procedure_type_concept_id": procedure_type_concept_id,
                "modifier_concept_id": modifier_concept_id,
                "quantity": quantity,
                # "provider_id": linked_provider_id,
                # "visit_occurrence_id": linked_visit_occurrence_id,
                # "visit_detail_id": None,
                "procedure_source_value": procedure_source_value,
                "procedure_source_concept_id": procedure_source_concept_id,
                # "modifier_source_value": modifier_source_value
            }
            omop_data["PROCEDURE_OCCURRENCE"].append(procedure_record)
            
        elif resource_type == "Observation":
            # Determine if it's a Measurement or Observation
            # Simple rule: 'laboratory' or 'vital-signs' category -> MEASUREMENT, else OBSERVATION
            maps_to_measurement = False
            if hasattr(resource, 'category') and resource.category:
                for cat_concept in resource.category:
                    if hasattr(cat_concept, 'coding') and cat_concept.coding:
                        for c in cat_concept.coding:
                            if c.system == "http://terminology.hl7.org/CodeSystem/observation-category":
                                if c.code in ["laboratory", "vital-signs"]:
                                    maps_to_measurement = True
                                    break
                        if maps_to_measurement:
                            break
            
            obs_concept_id = 0
            obs_source_value = None
            obs_source_concept_id = 0
            if hasattr(resource, 'code') and resource.code and hasattr(resource.code, 'coding') and resource.code.coding:
                # Prioritize LOINC, then SNOMED, then first available
                coding_to_use = None
                for c_system in ["http://loinc.org", "http://snomed.info/sct"]:
                    for c in resource.code.coding:
                        if c.system == c_system:
                            coding_to_use = c
                            break
                    if coding_to_use: break
                if not coding_to_use: coding_to_use = resource.code.coding[0]

                if coding_to_use and coding_to_use.system and coding_to_use.code:
                    mapping_info = _get_omop_standard_concept(coding_to_use.system, coding_to_use.code, session)
                    obs_concept_id = mapping_info["standard_concept_id"]
                    obs_source_value = mapping_info["source_value"]
                    obs_source_concept_id = mapping_info["source_concept_id"]

            obs_date = None
            obs_datetime = None
            if hasattr(resource, 'effectiveDateTime') and resource.effectiveDateTime:
                try:
                    dt_obj = datetime.fromisoformat(resource.effectiveDateTime.replace("Z", "+00:00"))
                    obs_date = dt_obj.date()
                    obs_datetime = dt_obj
                except ValueError:
                    print(f"Warning: Could not parse Observation effectiveDateTime '{resource.effectiveDateTime}'")
            elif hasattr(resource, 'effectivePeriod') and resource.effectivePeriod and hasattr(resource.effectivePeriod, 'start') and resource.effectivePeriod.start:
                try:
                    dt_obj = datetime.fromisoformat(resource.effectivePeriod.start.replace("Z", "+00:00"))
                    obs_date = dt_obj.date()
                    obs_datetime = dt_obj
                except ValueError:
                    print(f"Warning: Could not parse Observation effectivePeriod.start '{resource.effectivePeriod.start}'")

            value_as_number = None
            value_as_string = getattr(resource, 'valueString', None)
            value_as_concept_id = 0
            value_source_value = value_as_string # Default to valueString if present
            unit_concept_id = 0
            unit_source_value = None
            operator_concept_id = 0 # For comparators like <, >

            if hasattr(resource, 'valueQuantity') and resource.valueQuantity:
                vq = resource.valueQuantity
                if hasattr(vq, 'value'): value_as_number = vq.value
                if hasattr(vq, 'unit'): unit_source_value = vq.unit
                if hasattr(vq, 'code') and vq.code and hasattr(vq, 'system') and vq.system: # UCUM for units
                     # Try to map unit code to a standard OMOP unit concept
                    unit_mapping = _get_omop_standard_concept(vq.system, vq.code, session)
                    if unit_mapping["standard_concept_id"] != 0 : # Check if a valid mapping was found
                         unit_concept_id = unit_mapping["standard_concept_id"]
                    else: # Fallback if direct mapping not found, use source value
                        if not unit_source_value and vq.code : unit_source_value = vq.code


                if hasattr(vq, 'comparator') and vq.comparator:
                    comp_map = { "<": 4172704, "<=": 4171754, ">": 4172703, ">=": 4171755, "=": 0}
                    operator_concept_id = comp_map.get(vq.comparator, 0)
                
                if not value_source_value and value_as_number is not None: # If no string value, construct one
                    value_source_value = f"{vq.comparator or ''}{value_as_number} {unit_source_value or ''}".strip()


            if hasattr(resource, 'valueCodeableConcept') and resource.valueCodeableConcept:
                vc = resource.valueCodeableConcept
                if hasattr(vc, 'coding') and vc.coding:
                    # Try to map valueCodeableConcept to a standard concept
                    val_coding = vc.coding[0] # Take first
                    if val_coding.system and val_coding.code:
                        val_map_info = _get_omop_standard_concept(val_coding.system, val_coding.code, session)
                        value_as_concept_id = val_map_info["standard_concept_id"]
                        if not value_source_value: # If not already set by string or quantity
                            value_source_value = val_map_info["source_value"] or getattr(vc, 'text', None)
                elif hasattr(vc, 'text') and not value_source_value:
                     value_source_value = vc.text
            
            if hasattr(resource, 'valueBoolean') and resource.valueBoolean is not None:
                if not value_source_value: value_source_value = str(resource.valueBoolean)
                # Potentially map True/False to specific concept_ids if required by convention
                # For now, value_as_concept_id remains 0 unless a specific mapping is added

            if hasattr(resource, 'valueDateTime') and resource.valueDateTime:
                 if not value_source_value: value_source_value = resource.valueDateTime
                 # This might also go into observation_datetime if the main obs_datetime is different

            # Common fields
            common_record_fields = {
                # "person_id": linked_person_id,
                "observation_date": obs_date,
                "observation_datetime": obs_datetime,
                "value_as_string": value_as_string, # Retained for MEASUREMENT as well for source fidelity
                # "visit_occurrence_id": linked_visit_occurrence_id,
                # "provider_id": linked_provider_id,
            }

            if maps_to_measurement:
                measurement_record = {
                    **common_record_fields,
                    "measurement_concept_id": obs_concept_id,
                    "measurement_type_concept_id": 0, # e.g. 32817 From EHR, 44818702 Lab result
                    "operator_concept_id": operator_concept_id,
                    "value_as_number": value_as_number,
                    "value_as_concept_id": value_as_concept_id,
                    "unit_concept_id": unit_concept_id,
                    "range_low": getattr(resource.referenceRange[0].low, 'value', None) if hasattr(resource, 'referenceRange') and resource.referenceRange and hasattr(resource.referenceRange[0], 'low') else None,
                    "range_high": getattr(resource.referenceRange[0].high, 'value', None) if hasattr(resource, 'referenceRange') and resource.referenceRange and hasattr(resource.referenceRange[0], 'high') else None,
                    "measurement_source_value": obs_source_value,
                    "measurement_source_concept_id": obs_source_concept_id,
                    "unit_source_value": unit_source_value,
                    "value_source_value": value_source_value, # Value as originally recorded
                }
                # Rename observation_date/datetime to measurement_date/datetime for clarity if preferred by OMOP table
                measurement_record["measurement_date"] = measurement_record.pop("observation_date")
                measurement_record["measurement_datetime"] = measurement_record.pop("observation_datetime")
                omop_data["MEASUREMENT"].append(measurement_record)
            else: # Maps to OBSERVATION table
                observation_record = {
                    **common_record_fields,
                    "observation_concept_id": obs_concept_id,
                    "observation_type_concept_id": 0, # e.g. 38000280 EHR detail, 32817 From EHR
                    "value_as_number": value_as_number, # OBSERVATION table also has these
                    "value_as_concept_id": value_as_concept_id,
                    "qualifier_concept_id": 0, # From Observation.interpretation
                    "unit_concept_id": unit_concept_id, # OBSERVATION table also has this
                    "observation_source_value": obs_source_value,
                    "observation_source_concept_id": obs_source_concept_id,
                    "unit_source_value": unit_source_value,
                    "qualifier_source_value": None, # From Observation.interpretation.coding[0].code or text
                    "value_source_value": value_source_value, # Value as originally recorded
                    # "obs_event_field_concept_id" : 0 # If using observation_period relationship
                }
                omop_data["OBSERVATION"].append(observation_record)

    if session:
        session.close()

    return omop_data

def _get_omop_standard_concept(fhir_system: str, fhir_code: str, session):
    """
    Maps a FHIR code to a standard OMOP concept_id.

    Args:
        fhir_system (str): The URI of the FHIR coding system.
        fhir_code (str): The code from the FHIR resource.
        session: The SQLAlchemy session for database access.

    Returns:
        dict: A dictionary with 'standard_concept_id', 'source_concept_id', 
              and 'source_value', or None if no mapping found.
    """
    source_value = fhir_code
    source_concept_id = None
    standard_concept_id = None

    # 1. Map FHIR system URI to OMOP vocabulary_id
    # This mapping might need to be more sophisticated depending on the systems used.
    # For now, let's assume a simple mapping for common systems.
    vocabulary_id_map = {
        "http://my-custom-codes.org/fhir": "MyCustomCodes",
        "http://snomed.info/sct": "SNOMED",
        "http://loinc.org": "LOINC",
        "http://www.nlm.nih.gov/research/umls/rxnorm": "RxNorm",
        "http://hl7.org/fhir/sid/icd-10-cm": "ICD10CM",
        "http://hl7.org/fhir/sid/icd-9-cm": "ICD9CM" 
        # Add other mappings as needed
    }
    omop_vocabulary_id = vocabulary_id_map.get(fhir_system)

    if not omop_vocabulary_id:
        print(f"Warning: Unmapped FHIR system URI: {fhir_system}")
        return {"standard_concept_id": 0, "source_concept_id": 0, "source_value": source_value} # Default to 0 if unmapped

    try:
        # 2. Find Source Concept in OMOP CONCEPT table
        source_concept_query = session.query(omop54.Concept).filter(
            omop54.Concept.vocabulary_id == omop_vocabulary_id,
            omop54.Concept.concept_code == fhir_code
        )
        source_concept_result = source_concept_query.first()

        if source_concept_result:
            source_concept_id = source_concept_result.concept_id
            
            # 3. Find Standard Concept using CONCEPT_RELATIONSHIP table
            # Looking for 'Maps to' relationship
            standard_concept_query = session.query(omop54.ConceptRelationship).filter(
                omop54.ConceptRelationship.concept_id_1 == source_concept_id,
                omop54.ConceptRelationship.relationship_id == 'Maps to' 
                # Ensure 'Maps to' is the correct relationship_id string in your OMOP vocab
            )
            standard_concept_relationship = standard_concept_query.first()

            if standard_concept_relationship:
                standard_concept_id = standard_concept_relationship.concept_id_2
            else:
                # If no direct 'Maps to' relationship, the source concept might already be standard
                # or it might map to itself, or it might be non-standard without a direct map.
                # For simplicity, if no 'Maps to', check if source is standard.
                if source_concept_result.standard_concept == 'S':
                     standard_concept_id = source_concept_id
                else:
                    print(f"Warning: No 'Maps to' relationship found for source_concept_id: {source_concept_id} ({fhir_system}|{fhir_code})")
                    standard_concept_id = 0 # Default to 0 if no standard mapping
        else:
            print(f"Warning: Source concept not found for {fhir_system}|{fhir_code}")
            standard_concept_id = 0 # Default to 0 if source not found
            source_concept_id = 0

        return {
            "standard_concept_id": standard_concept_id if standard_concept_id is not None else 0,
            "source_concept_id": source_concept_id if source_concept_id is not None else 0,
            "source_value": source_value
        }

    except Exception as e:
        print(f"Error during vocabulary mapping for {fhir_system}|{fhir_code}: {str(e)}")
        return {"standard_concept_id": 0, "source_concept_id": 0, "source_value": source_value}

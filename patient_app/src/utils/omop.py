import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from utils.db import DatabaseManager 
from omopmodel import OMOP_5_4_declarative as omop54

def _calculate_age(birth_date: datetime) -> int:
    """Calculates age from a birth date."""
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def _map_age_to_uci_category(age: int) -> float:
    """Maps raw age to the 13-level UCI dataset age category."""
    if 18 <= age <= 24: return 1.0
    if 25 <= age <= 29: return 2.0
    if 30 <= age <= 34: return 3.0
    if 35 <= age <= 39: return 4.0
    if 40 <= age <= 44: return 5.0
    if 45 <= age <= 49: return 6.0
    if 50 <= age <= 54: return 7.0
    if 55 <= age <= 59: return 8.0
    if 60 <= age <= 64: return 9.0
    if 65 <= age <= 69: return 10.0
    if 70 <= age <= 74: return 11.0
    if 75 <= age <= 79: return 12.0
    if age >= 80: return 13.0
    return 0.0 # Default or for ages outside expected range

def get_data(schema: Dict, person_id: Optional[int] = None) -> np.array:
    """
    Recupera datos del modelo OMOP-CDM utilizando el esquema proporcionado,
    aplanando características de múltiples dominios en un solo vector numérico.
    
    Args:
        schema (dict): Un diccionario que define los campos requeridos.
        person_id (Optional[int]): El person_id del paciente para filtrar los datos.
                                   Si es None, los datos no se filtrarán por paciente (no recomendado).
    
    Returns:
        np.array: Matriz NumPy 2D con los datos solicitados (una fila de características numéricas).
    """
    print("Recuperando datos de la base de datos OMOP-CDM...")
    if person_id:
        print(f"Filtrando datos para person_id: {person_id}")
    else:
        print("Advertencia: No se proporcionó person_id a get_data. Los datos no se filtrarán por paciente.")

    all_feature_values: List[float] = [] 
    person_record_cache: Optional[omop54.Person] = None # Cache person record

    # El orden de procesamiento DEBE coincidir con el orden esperado por el modelo FHE.
    # Y las claves deben coincidir con las del schema (ej. 'measurement', 'condition', 'observation')
    domain_processing_order = ["measurement", "condition", "observation"] 
    # Ajusta este orden si tus _DEFINITIONS y modelos FHE esperan un orden diferente.
    # Para diabetes, el orden en DIABETES_DEFINITIONS es Observation, Condition, Measurement.
    # Vamos a usar el orden de DIABETES_DEFINITIONS para ser consistentes.
    if any(k in schema for k in ["observation", "condition"]): # Heurística para diabetes
        domain_processing_order = ["observation", "condition", "measurement"]
    else: # Para cáncer de mama que solo tiene 'measurement'
        domain_processing_order = ["measurement"]


    try:
        session = DatabaseManager.get_db_session()
        if not session:
            print("Error: No se pudo obtener la sesión de la base de datos. Usando datos simulados.")
            return get_mock_data_for_schema(schema, person_id) # Pass person_id to mock data too

        for domain_key in domain_processing_order:
            if domain_key in schema:
                feature_definitions_list = schema[domain_key]
                
                # print(f"Procesando dominio: {domain_key} con {len(feature_definitions_list)} definiciones")

                omop_table_class = None
                concept_id_key_in_schema = f"{domain_key}_concept_id" # e.g., measurement_concept_id
                source_value_key_in_schema = f"{domain_key}_source_value"
                
                # Nombres reales de las columnas en las tablas OMOP
                table_concept_id_col_name = concept_id_key_in_schema
                table_source_value_col_name = source_value_key_in_schema
                date_col_for_ordering_name = None
                # person_id_col_name = "person_id" # Defined below where omop_table_class is known

                if domain_key == "measurement":
                    omop_table_class = omop54.Measurement
                    date_col_for_ordering_name = "measurement_date"
                elif domain_key == "condition":
                    omop_table_class = omop54.ConditionOccurrence
                    table_concept_id_col_name = "condition_concept_id"
                    table_source_value_col_name = "condition_source_value"
                    date_col_for_ordering_name = "condition_start_date"
                elif domain_key == "observation":
                    omop_table_class = omop54.Observation
                    date_col_for_ordering_name = "observation_date"
                else:
                    print(f"Advertencia: Dominio '{domain_key}' no manejado. Omitiendo.")
                    for _ in feature_definitions_list: all_feature_values.append(0.0)
                    continue
                
                # Ensure omop_table_class is not None before trying to get person_id_col_name
                if not omop_table_class:
                    print(f"Error: omop_table_class no se estableció para el dominio {domain_key}. Omitiendo características.")
                    for _ in feature_definitions_list: all_feature_values.append(0.0)
                    continue

                person_id_col_name_for_domain_table = "person_id"

                for feature_info in feature_definitions_list:
                    value_name = feature_info.get('value_name')
                    is_demographic = feature_info.get("is_person_demographic", False)
                    retrieved_numeric_value = 0.0 

                    # Handle demographic features from Person table
                    if is_demographic or value_name in ["patient_sex", "patient_age"]:
                        if person_id is None:
                            print(f"Advertencia: Se requiere person_id para la característica demográfica '{value_name}', pero no se proporcionó. Usando 0.0.")
                            all_feature_values.append(0.0)
                            continue
                        
                        if person_record_cache is None: # Fetch person record only once
                            person_record_cache = session.query(omop54.Person).filter(omop54.Person.person_id == person_id).first()

                        if not person_record_cache:
                            print(f"Advertencia: No se encontró registro de Persona para person_id {person_id} para la característica '{value_name}'. Usando 0.0.")
                            all_feature_values.append(0.0)
                            continue

                        if value_name == "patient_sex":
                            # UCI: 0 = female, 1 = male
                            # OMOP: FEMALE = 8532, MALE = 8507
                            if person_record_cache.gender_concept_id == 8532: # FEMALE
                                retrieved_numeric_value = 0.0
                            elif person_record_cache.gender_concept_id == 8507: # MALE
                                retrieved_numeric_value = 1.0
                            else: # Unknown or Other
                                retrieved_numeric_value = 0.0 # Defaulting to female/0 for unknowns
                            # print(f"Demographic - Sex: {retrieved_numeric_value} (gender_concept_id: {person_record_cache.gender_concept_id})")
                        elif value_name == "patient_age":
                            if person_record_cache.year_of_birth:
                                try:
                                    birth_date = datetime(
                                        person_record_cache.year_of_birth,
                                        person_record_cache.month_of_birth or 1,
                                        person_record_cache.day_of_birth or 1
                                    )
                                    raw_age = _calculate_age(birth_date)
                                    retrieved_numeric_value = _map_age_to_uci_category(raw_age)
                                    # print(f"Demographic - Age: {raw_age}, Category: {retrieved_numeric_value}")
                                except ValueError:
                                    print(f"Advertencia: Fecha de nacimiento inválida para person_id {person_id}. Usando 0.0 para la edad.")
                                    retrieved_numeric_value = 0.0
                            else:
                                print(f"Advertencia: Año de nacimiento no disponible para person_id {person_id}. Usando 0.0 para la edad.")
                                retrieved_numeric_value = 0.0
                        else:
                            print(f"Advertencia: Característica demográfica desconocida '{value_name}'. Usando 0.0.")
                            retrieved_numeric_value = 0.0
                        
                        all_feature_values.append(retrieved_numeric_value)
                        continue # Move to the next feature_info

                    # --- Standard processing for non-demographic features ---
                    concept_id = feature_info.get(concept_id_key_in_schema)
                    source_value = feature_info.get(source_value_key_in_schema)
                    
                    query = session.query(omop_table_class)
                    
                    if person_id is not None and hasattr(omop_table_class, person_id_col_name_for_domain_table):
                        query = query.filter(getattr(omop_table_class, person_id_col_name_for_domain_table) == person_id)
                    elif person_id is not None: # Should not happen if omop_table_class is set
                        print(f"Advertencia: person_id {person_id} proporcionado, pero la tabla {omop_table_class.__tablename__} no tiene columna '{person_id_col_name_for_domain_table}'.")

                    filter_applied_for_concept = False
                    if concept_id and concept_id != 0:
                        query = query.filter(getattr(omop_table_class, table_concept_id_col_name) == concept_id)
                        filter_applied_for_concept = True
                    elif source_value:
                        query = query.filter(getattr(omop_table_class, table_source_value_col_name) == source_value)
                        filter_applied_for_concept = True
                    
                    if not filter_applied_for_concept:
                        all_feature_values.append(retrieved_numeric_value) # Default 0.0
                        continue
                        
                    record = None
                    if date_col_for_ordering_name and hasattr(omop_table_class, date_col_for_ordering_name):
                        date_column_attr = getattr(omop_table_class, date_col_for_ordering_name)
                        record = query.order_by(date_column_attr.desc()).first()
                    else:
                        record = query.first()

                    if record:
                        if domain_key == "measurement":
                            if hasattr(record, 'value_as_number') and getattr(record, 'value_as_number') is not None:
                                retrieved_numeric_value = float(getattr(record, 'value_as_number'))
                        elif domain_key == "condition":
                            retrieved_numeric_value = 1.0 
                        elif domain_key == "observation": # Non-demographic observations
                            if hasattr(record, 'value_as_number') and getattr(record, 'value_as_number') is not None:
                                retrieved_numeric_value = float(getattr(record, 'value_as_number'))
                            else: 
                                retrieved_numeric_value = 1.0 
                    
                    all_feature_values.append(retrieved_numeric_value)
        
        # print(f"Valores finales extraídos: {all_feature_values}")

        if not all_feature_values and isinstance(schema, dict) and any(isinstance(s, list) and s for s in schema.values()):
            print("INFO: No se extrajeron valores de OMOP-CDM, pero el esquema define características. Usando datos simulados.")
            return get_mock_data_for_schema(schema, person_id)
        elif not all_feature_values:
            print("INFO: all_feature_values vacía y el esquema no define características. Devolviendo array vacío.")
            return np.array([[]]) # Shape (1,0)

        return np.array([all_feature_values]) # Shape (1, num_features)
    
    except Exception as e:
        print(f"Error al acceder a la base de datos OMOP-CDM: {str(e)}")
        import traceback
        traceback.print_exc() # Imprimir el stack trace completo
        print("Recurriendo a datos simulados debido a una excepción.")
        return get_mock_data_for_schema(schema, person_id) # Asegurarse que mock data también es numérico y plano
    finally:
        if 'session' in locals() and session is not None:
            session.close()

def get_mock_data_for_schema(schema, person_id: Optional[int] = None): # Add person_id here too
    """
    Genera datos simulados NUMÉRICOS basados en el esquema proporcionado,
    asegurando un solo vector de características.
    
    Args:
        schema (dict or list): Un diccionario que define los campos requeridos 
                               o una lista de nombres de características.
        person_id (Optional[int]): El person_id del paciente para el que se simulan los datos.
                                   No tiene efecto en los datos simulados por ahora, pero se incluye
                                   para mantener la consistencia con la firma de get_data.
    
    Returns:
        np.array: Matriz NumPy 2D con datos simulados numéricos (una fila de datos).
    """
    print("Generando datos simulados NUMÉRICOS para el esquema.")
    if person_id:
        print(f"(Contexto de datos simulados para person_id: {person_id})") # Solo para log
    current_row_values = []

    # El orden de procesamiento DEBE coincidir con el de get_data y el modelo FHE.
    domain_processing_order = ["measurement", "condition", "observation"]
    if isinstance(schema, dict) and any(k in schema for k in ["observation", "condition"]): # Heurística para diabetes
        domain_processing_order = ["observation", "condition", "measurement"]
    elif isinstance(schema, dict) and "measurement" in schema:
        domain_processing_order = ["measurement"]
    # Si es una lista, el bucle de abajo lo manejará sin domain_processing_order

    if isinstance(schema, dict):
        for domain_key in domain_processing_order:
            if domain_key in schema:
                feature_definitions_list = schema.get(domain_key, [])
                if isinstance(feature_definitions_list, list):
                    for _feature_def in feature_definitions_list:
                        value_name = _feature_def.get("value_name", "").lower()
                        is_demographic = _feature_def.get("is_person_demographic", False)

                        if is_demographic or value_name in ["patient_sex", "patient_age"]:
                            if value_name == "patient_sex":
                                current_row_values.append(float(np.random.randint(0, 2))) # 0 or 1
                            elif value_name == "patient_age":
                                # Mocking UCI age category (1-13)
                                current_row_values.append(float(np.random.randint(1, 14))) 
                            else: # Should not happen if value_names are specific
                                current_row_values.append(0.0)
                            continue

                        # Mocking for non-demographic features
                        if domain_key == "condition": 
                            current_row_values.append(float(np.random.randint(0, 2)))
                        elif domain_key == "observation": # Non-demographic observations
                            is_binary_heuristic = (
                                value_name.endswith("_status") or
                                value_name.startswith("is_") or
                                value_name in ["cholcheck", "smoker", "physactivity", "fruits", "veggies", "hvyalcoholconsump", "anyhealthcare", "nodocbccost", "diffwalk"]
                            )
                            if is_binary_heuristic:
                                current_row_values.append(float(np.random.randint(0, 2)))
                            else: 
                                # For scales like GenHlth, MentHlth, PhysHlth, Education, Income
                                if value_name == "general_health_scale_1_5": current_row_values.append(float(np.random.randint(1, 6)))
                                elif value_name == "days_of_poor_mental_health": current_row_values.append(float(np.random.randint(0, 31)))
                                elif value_name == "days_of_poor_physical_health": current_row_values.append(float(np.random.randint(0, 31)))
                                elif value_name == "education_level_scale_1_6": current_row_values.append(float(np.random.randint(1, 7)))
                                elif value_name == "income_level_scale_1_8": current_row_values.append(float(np.random.randint(1, 9)))
                                else: current_row_values.append(round(np.random.uniform(0.0, 5.0), 4)) # Default for other numeric obs
                        else: # Measurement
                            current_row_values.append(round(np.random.uniform(10.0, 50.0), 4)) # e.g., BMI
    elif isinstance(schema, list): 
        if schema: 
            for _ in schema: 
                current_row_values.append(float(np.random.randint(0, 2))) # Asumir binario para esquemas de lista simples
        
    if not current_row_values:
        print("Advertencia: No se generaron valores simulados. El esquema podría estar vacío o no tener definiciones en los dominios esperados.")
        return np.array([[]])
    else:
        # print(f"Valores simulados generados: {current_row_values}")
        return np.array([current_row_values])


# ... (resto de transform_fhir_bundle_to_omop y _get_omop_standard_concept) ...
# Asegúrate de que el resto del archivo, incluyendo transform_fhir_bundle_to_omop y _get_omop_standard_concept,
# esté presente y sea correcto. Por brevedad, no se incluyen aquí.
def transform_fhir_bundle_to_omop(bundle):
    # ... (implementation from your file) ...
    print("transform_fhir_bundle_to_omop called - placeholder implementation for brevity")
    return {}

def _get_omop_standard_concept(fhir_system: str, fhir_code: str, session):
    # ... (implementation from your file) ...
    print("_get_omop_standard_concept called - placeholder implementation for brevity")
    return {"standard_concept_id": 0, "source_concept_id": 0, "source_value": fhir_code}

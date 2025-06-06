import numpy as np
from sqlalchemy.orm import Session
from db.database import db_session, engine
from db.models import (
    Person, 
    Observation,
    Measurement, 
    Concept,
    Vocabulary,
    ConditionOccurrence,
    DrugExposure,
    ProcedureOccurrence,
    VisitOccurrence
)
from datetime import datetime

def get_db_session():
    """
    Obtiene una sesión de la base de datos.
    """
    return db_session

def initialize_database():
    """
    Inicializa la base de datos creando todas las tablas.
    """
    from .db.database import Base
    Base.metadata.create_all(bind=engine)
    print("Base de datos OMOP-CDM inicializada correctamente")

def get_patient_by_id(patient_id):
    """
    Obtiene un paciente por su ID.
    
    Args:
        patient_id (int): ID del paciente (person_id)
        
    Returns:
        Person: Objeto Person si se encuentra, None en caso contrario
    """
    try:
        session = get_db_session()
        return session.query(Person).filter(Person.person_id == patient_id).first()
    except Exception as e:
        print(f"Error al obtener el paciente: {str(e)}")
        return None

def get_patient_conditions(patient_id):
    """
    Obtiene las condiciones médicas de un paciente.
    
    Args:
        patient_id (int): ID del paciente (person_id)
        
    Returns:
        list: Lista de condiciones del paciente
    """
    try:
        session = get_db_session()
        conditions = session.query(ConditionOccurrence).filter(
            ConditionOccurrence.person_id == patient_id
        ).all()
        return conditions
    except Exception as e:
        print(f"Error al obtener las condiciones del paciente: {str(e)}")
        return []

def get_patient_medications(patient_id):
    """
    Obtiene los medicamentos de un paciente.
    
    Args:
        patient_id (int): ID del paciente (person_id)
        
    Returns:
        list: Lista de medicamentos del paciente
    """
    try:
        session = get_db_session()
        medications = session.query(DrugExposure).filter(
            DrugExposure.person_id == patient_id
        ).all()
        return medications
    except Exception as e:
        print(f"Error al obtener los medicamentos del paciente: {str(e)}")
        return []

def get_patient_procedures(patient_id):
    """
    Obtiene los procedimientos realizados a un paciente.
    
    Args:
        patient_id (int): ID del paciente (person_id)
        
    Returns:
        list: Lista de procedimientos del paciente
    """
    try:
        session = get_db_session()
        procedures = session.query(ProcedureOccurrence).filter(
            ProcedureOccurrence.person_id == patient_id
        ).all()
        return procedures
    except Exception as e:
        print(f"Error al obtener los procedimientos del paciente: {str(e)}")
        return []

def get_patient_visits(patient_id):
    """
    Obtiene las visitas médicas de un paciente.
    
    Args:
        patient_id (int): ID del paciente (person_id)
        
    Returns:
        list: Lista de visitas del paciente
    """
    try:
        session = get_db_session()
        visits = session.query(VisitOccurrence).filter(
            VisitOccurrence.person_id == patient_id
        ).all()
        return visits
    except Exception as e:
        print(f"Error al obtener las visitas del paciente: {str(e)}")
        return []

def get_concept_name(concept_id):
    """
    Obtiene el nombre de un concepto por su ID.
    
    Args:
        concept_id (int): ID del concepto
        
    Returns:
        str: Nombre del concepto o None si no se encuentra
    """
    try:
        session = get_db_session()
        concept = session.query(Concept).filter(Concept.concept_id == concept_id).first()
        if concept:
            return concept.concept_name
        return None
    except Exception as e:
        print(f"Error al obtener el nombre del concepto: {str(e)}")
        return None

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
    
    # Función de respaldo para datos simulados cuando la base de datos aún no contiene datos
    def get_mock_data():
        if schema and all(key in schema for key in [
            "radius1", "texture1", "perimeter1", "area1", "smoothness1", "compactness1", "concavity1", 
            "concave_points1", "symmetry1", "fractal_dimension1", "radius2", "texture2", "perimeter2", 
            "area2", "smoothness2", "compactness2", "concavity2", "concave_points2", "symmetry2", 
            "fractal_dimension2", "radius3", "texture3", "perimeter3", "area3", "smoothness3", 
            "compactness3", "concavity3", "concave_points3", "symmetry3", "fractal_dimension3"
            ]):
            return np.array([[13.54, 14.36, 87.46, 566.3, 0.09779, 0.08129, 0.06664, 0.04781, 0.1885, 0.05766,
                          0.2699, 0.7886, 2.058, 23.56, 0.008462, 0.01460, 0.02387, 0.01315, 0.01980, 0.002300,
                          15.11, 19.26, 99.70, 711.2, 0.14400, 0.17730, 0.23900, 0.12880, 0.2977, 0.07259]])
        elif schema and all(key in schema for key in [
            "HighBP", "HighChol", "CholCheck", "BMI", "Smoker", "Stroke", 
            "HeartDiseaseorAttack", "PhysActivity", "Fruits", "Veggies", 
            "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost", "GenHlth", 
            "MentHlth", "PhysHlth", "DiffWalk", "Sex", "Age", "Education", "Income"
            ]):
            return np.array([[
                1,  # HighBP (presión alta)
                0,  # HighChol (sin colesterol alto)
                1,  # CholCheck (chequeo de colesterol realizado)
                25, # BMI (índice de masa corporal)
                0,  # Smoker (no fumador)
                0,  # Stroke (sin historial de derrame cerebral)
                0,  # HeartDiseaseorAttack (sin enfermedad cardíaca)
                1,  # PhysActivity (actividad física realizada)
                1,  # Fruits (consume frutas diariamente)
                1,  # Veggies (consume vegetales diariamente)
                0,  # HvyAlcoholConsump (no consumo excesivo de alcohol)
                1,  # AnyHealthcare (tiene cobertura médica)
                0,  # NoDocbcCost (no tuvo problemas para pagar al médico)
                3,  # GenHlth (salud general: 3 = buena)
                2,  # MentHlth (días con problemas de salud mental en el último mes)
                0,  # PhysHlth (días con problemas de salud física en el último mes)
                0,  # DiffWalk (sin dificultad para caminar)
                1,  # Sex (1 = masculino)
                35, # Age (categoría de edad, por ejemplo, 35 = 35-39 años)
                4,  # Education (nivel educativo: 4 = graduado universitario)
                6   # Income (nivel de ingresos: 6 = $50,000-$74,999)
            ]])
        else:
            return None
    
    try:
        session = get_db_session()
        
        # Intenta obtener datos de la base de datos real
        if schema and all(key in schema for key in [
            "radius1", "texture1", "perimeter1", "area1", "smoothness1", "compactness1", "concavity1", 
            "concave_points1", "symmetry1", "fractal_dimension1", "radius2", "texture2", "perimeter2", 
            "area2", "smoothness2", "compactness2", "concavity2", "concave_points2", "symmetry2", 
            "fractal_dimension2", "radius3", "texture3", "perimeter3", "area3", "smoothness3", 
            "compactness3", "concavity3", "concave_points3", "symmetry3", "fractal_dimension3"
            ]):
            # Intentar obtener mediciones de cáncer de mama utilizando el modelo OMOP-CDM
            # Aquí deberíamos tener códigos de concepto específicos para estas medidas
            data = get_mock_data()  # Usar datos simulados hasta que tengamos datos reales
            return data
            
        elif schema and all(key in schema for key in [
            "HighBP", "HighChol", "CholCheck", "BMI", "Smoker", "Stroke", 
            "HeartDiseaseorAttack", "PhysActivity", "Fruits", "Veggies", 
            "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost", "GenHlth", 
            "MentHlth", "PhysHlth", "DiffWalk", "Sex", "Age", "Education", "Income"
            ]):
            # Intentar obtener observaciones y mediciones de indicadores de salud para diabetes
            # Aquí deberíamos tener códigos de concepto específicos para estas medidas
            data = get_mock_data()  # Usar datos simulados hasta que tengamos datos reales
            return data
        
        # Si llegamos aquí, significa que no pudimos encontrar los datos en la base de datos real
        mock_data = get_mock_data()
        if mock_data is not None:
            return mock_data
        else:
            raise ValueError("Esquema inválido proporcionado o datos no encontrados.")
    
    except Exception as e:
        print(f"Error al acceder a la base de datos OMOP-CDM: {str(e)}")
        # En caso de error, intentamos volver a los datos simulados
        mock_data = get_mock_data()
        if mock_data is not None:
            return mock_data
        else:
            raise ValueError("Esquema inválido proporcionado o datos no encontrados.")

def save_measurement_from_fhir(obs, patient_id: str):
    """
    Mapea un Observation FHIR a un registro OMOP Measurement y lo almacena.
    """
    session = get_db_session()
    # Mapear código LOINC a OMOP concept_id
    loinc_code = obs.code.coding[0].code
    concept = session.query(Concept).filter(
        Concept.vocabulary_id == 'LOINC',
        Concept.concept_code == loinc_code
    ).first()
    m_concept_id = concept.concept_id if concept else None

    # Mapear unidad UCUM a OMOP concept_id
    unit_code = getattr(obs.valueQuantity, 'code', None)
    unit_concept = None
    if unit_code:
        unit_concept = session.query(Concept).filter(
            Concept.vocabulary_id == 'UCUM',
            Concept.concept_code == unit_code
        ).first()
    u_concept_id = unit_concept.concept_id if unit_concept else None

    # Crear y guardar Measurement
    m = Measurement(
        person_id=int(patient_id),
        measurement_concept_id=m_concept_id,
        measurement_date=obs.effectiveDateTime.date(),
        measurement_datetime=datetime.fromisoformat(obs.effectiveDateTime),
        measurement_type_concept_id=44818701,  # e.g. "FHIR Observation"
        value_as_number=obs.valueQuantity.value,
        unit_concept_id=u_concept_id,
        unit_source_value=unit_code,
        value_source_value=str(obs.valueQuantity.value)
    )
    session.add(m)
    session.commit()
    print(f"Measurement OMOP guardado: concept_id={m_concept_id}, valor={m.value_as_number}")

def get_mock_value(feature: str):
    """
    Retorna el valor simulado para un feature dado, usando los mock_data internal.
    """
    # Buscar en los mock_data hardcodeados
    # Breast cancer
    bc_schema = [
        "radius1","texture1","perimeter1","area1","smoothness1","compactness1","concavity1","concave_points1","symmetry1","fractal_dimension1",
        "radius2","texture2","perimeter2","area2","smoothness2","compactness2","concavity2","concave_points2","symmetry2","fractal_dimension2",
        "radius3","texture3","perimeter3","area3","smoothness3","compactness3","concavity3","concave_points3","symmetry3","fractal_dimension3"
    ]
    bc_values = [
        13.54,14.36,87.46,566.3,0.09779,0.08129,0.06664,0.04781,0.1885,0.05766,
        0.2699,0.7886,2.058,23.56,0.008462,0.01460,0.02387,0.01315,0.01980,0.002300,
        15.11,19.26,99.70,711.2,0.14400,0.17730,0.23900,0.12880,0.2977,0.07259
    ]
    dm_schema = [
        "HighBP","HighChol","CholCheck","BMI","Smoker","Stroke","HeartDiseaseorAttack",
        "PhysActivity","Fruits","Veggies","HvyAlcoholConsump","AnyHealthcare","NoDocbcCost",
        "GenHlth","MentHlth","PhysHlth","DiffWalk","Sex","Age","Education","Income"
    ]
    dm_values = [
        1,0,1,25,0,0,0,1,1,1,0,1,0,3,2,0,0,1,35,4,6
    ]
    if feature in bc_schema:
        return bc_values[bc_schema.index(feature)]
    if feature in dm_schema:
        return dm_values[dm_schema.index(feature)]
    return None
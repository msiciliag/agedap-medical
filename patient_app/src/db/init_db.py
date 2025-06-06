"""
Script para inicializar la base de datos OMOP-CDM y cargar datos de ejemplo.
"""
import datetime
import os
import sys

# Agrega el directorio raíz al path de Python para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.database import Base, engine, db_session
from src.db.models import (
    Person, 
    Concept,
    Vocabulary,
    Domain,
    ConceptClass,
    Relationship,
    VisitOccurrence,
    ConditionOccurrence,
    Measurement,
    Observation,
    DrugExposure,
    Provider,
    CareSite,
    Location
)

def initialize_database():
    """
    Inicializa la base de datos creando todas las tablas definidas en los modelos.
    """
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas con éxito.")

def create_essential_concept_records():
    """
    Crea registros básicos de vocabulario necesarios para el funcionamiento del modelo OMOP-CDM.
    """
    print("Creando registros básicos de vocabulario...")
    
    # Verificar si ya existen registros para evitar duplicados
    session = db_session()
    
    # Crear vocabularios
    vocab_count = session.query(Vocabulary).count()
    if vocab_count == 0:
        snomed_vocab = Vocabulary(
            vocabulary_id="SNOMED",
            vocabulary_name="Systematized Nomenclature of Medicine - Clinical Terms",
            vocabulary_reference="http://www.snomed.org/",
            vocabulary_version="2021",
            vocabulary_concept_id=1
        )
        loinc_vocab = Vocabulary(
            vocabulary_id="LOINC",
            vocabulary_name="Logical Observation Identifiers Names and Codes",
            vocabulary_reference="http://loinc.org/",
            vocabulary_version="2.71",
            vocabulary_concept_id=2
        )
        rxnorm_vocab = Vocabulary(
            vocabulary_id="RxNorm",
            vocabulary_name="RxNorm",
            vocabulary_reference="http://www.nlm.nih.gov/research/umls/rxnorm/",
            vocabulary_version="20210104",
            vocabulary_concept_id=3
        )
        session.add_all([snomed_vocab, loinc_vocab, rxnorm_vocab])
    
    # Crear dominios
    domain_count = session.query(Domain).count()
    if domain_count == 0:
        condition_domain = Domain(
            domain_id="Condition",
            domain_name="Condition",
            domain_concept_id=1000
        )
        drug_domain = Domain(
            domain_id="Drug",
            domain_name="Drug",
            domain_concept_id=1001
        )
        measurement_domain = Domain(
            domain_id="Measurement",
            domain_name="Measurement",
            domain_concept_id=1002
        )
        observation_domain = Domain(
            domain_id="Observation",
            domain_name="Observation",
            domain_concept_id=1003
        )
        session.add_all([condition_domain, drug_domain, measurement_domain, observation_domain])
    
    # Crear clases de concepto
    concept_class_count = session.query(ConceptClass).count()
    if concept_class_count == 0:
        clinical_finding = ConceptClass(
            concept_class_id="Clinical Finding",
            concept_class_name="Clinical Finding",
            concept_class_concept_id=2000
        )
        medication = ConceptClass(
            concept_class_id="Medication",
            concept_class_name="Medication",
            concept_class_concept_id=2001
        )
        lab_test = ConceptClass(
            concept_class_id="Lab Test",
            concept_class_name="Lab Test",
            concept_class_concept_id=2002
        )
        session.add_all([clinical_finding, medication, lab_test])
    
    # Crear relaciones
    relationship_count = session.query(Relationship).count()
    if relationship_count == 0:
        is_a = Relationship(
            relationship_id="Is a",
            relationship_name="Is a",
            is_hierarchical="1",
            defines_ancestry="1",
            relationship_concept_id=3000
        )
        has_ingredient = Relationship(
            relationship_id="Has ingredient",
            relationship_name="Has ingredient",
            is_hierarchical="0",
            defines_ancestry="0",
            relationship_concept_id=3001
        )
        session.add_all([is_a, has_ingredient])
    
    # Crear conceptos básicos necesarios para el esquema
    concept_count = session.query(Concept).count()
    if concept_count == 0:
        # Conceptos para persona
        gender_male = Concept(
            concept_id=8507,
            concept_name="Male",
            domain_id="Gender",
            vocabulary_id="SNOMED",
            concept_class_id="Clinical Finding",
            standard_concept="S",
            concept_code="248153007",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        gender_female = Concept(
            concept_id=8532,
            concept_name="Female",
            domain_id="Gender",
            vocabulary_id="SNOMED",
            concept_class_id="Clinical Finding",
            standard_concept="S",
            concept_code="248152002",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        
        # Conceptos para condiciones
        diabetes = Concept(
            concept_id=201826,
            concept_name="Type 2 diabetes mellitus",
            domain_id="Condition",
            vocabulary_id="SNOMED",
            concept_class_id="Clinical Finding",
            standard_concept="S",
            concept_code="44054006",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        hypertension = Concept(
            concept_id=320128,
            concept_name="Essential hypertension",
            domain_id="Condition",
            vocabulary_id="SNOMED",
            concept_class_id="Clinical Finding",
            standard_concept="S",
            concept_code="59621000",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        
        # Conceptos para medicamentos
        metformin = Concept(
            concept_id=1503297,
            concept_name="Metformin",
            domain_id="Drug",
            vocabulary_id="RxNorm",
            concept_class_id="Medication",
            standard_concept="S",
            concept_code="6809",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        lisinopril = Concept(
            concept_id=1308216,
            concept_name="Lisinopril",
            domain_id="Drug",
            vocabulary_id="RxNorm",
            concept_class_id="Medication",
            standard_concept="S",
            concept_code="29046",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        
        # Conceptos para mediciones
        blood_glucose = Concept(
            concept_id=3004501,
            concept_name="Glucose [Mass/volume] in Blood",
            domain_id="Measurement",
            vocabulary_id="LOINC",
            concept_class_id="Lab Test",
            standard_concept="S",
            concept_code="2339-0",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        blood_pressure = Concept(
            concept_id=3004249,
            concept_name="Blood pressure",
            domain_id="Measurement",
            vocabulary_id="LOINC",
            concept_class_id="Lab Test",
            standard_concept="S",
            concept_code="55284-4",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        
        # Conceptos para tipos de datos
        ehr_record = Concept(
            concept_id=32817,
            concept_name="EHR record",
            domain_id="Type Concept",
            vocabulary_id="SNOMED",
            concept_class_id="Record Type",
            standard_concept="S",
            concept_code="32817",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        
        # Conceptos para visitas
        outpatient_visit = Concept(
            concept_id=9202,
            concept_name="Outpatient Visit",
            domain_id="Visit",
            vocabulary_id="SNOMED",
            concept_class_id="Visit",
            standard_concept="S",
            concept_code="9202",
            valid_start_date=datetime.date(2000, 1, 1),
            valid_end_date=datetime.date(2099, 12, 31)
        )
        
        session.add_all([
            gender_male, gender_female, diabetes, hypertension, metformin, 
            lisinopril, blood_glucose, blood_pressure, ehr_record, outpatient_visit
        ])
    
    session.commit()
    session.close()
    
    print("Registros básicos de vocabulario creados con éxito.")

def create_sample_person():
    """
    Crea registros de persona de ejemplo.
    """
    print("Creando registros de persona de ejemplo...")
    
    session = db_session()
    
    # Verificar si ya existen personas
    person_count = session.query(Person).count()
    if person_count == 0:
        # Crear locación
        location = Location(
            location_id=1,
            address_1="123 Main St",
            city="Example City",
            state="NY",
            zip="10001"
        )
        session.add(location)
        session.flush()
        
        # Crear sitio de atención
        care_site = CareSite(
            care_site_id=1,
            care_site_name="Example Medical Center",
            place_of_service_concept_id=9202,
            location_id=1
        )
        session.add(care_site)
        session.flush()
        
        # Crear proveedor
        provider = Provider(
            provider_id=1,
            provider_name="Dr. Example",
            specialty_concept_id=38004456,  # Médico de familia
            care_site_id=1
        )
        session.add(provider)
        session.flush()
        
        # Crear personas
        person1 = Person(
            person_id=1,
            gender_concept_id=8507,  # Masculino
            year_of_birth=1975,
            month_of_birth=6,
            day_of_birth=15,
            birth_datetime=datetime.datetime(1975, 6, 15),
            race_concept_id=8527,  # Blanco
            ethnicity_concept_id=38003564,  # No hispano
            location_id=1,
            provider_id=1,
            care_site_id=1,
            person_source_value="PT001"
        )
        
        person2 = Person(
            person_id=2,
            gender_concept_id=8532,  # Femenino
            year_of_birth=1982,
            month_of_birth=3,
            day_of_birth=21,
            birth_datetime=datetime.datetime(1982, 3, 21),
            race_concept_id=8527,  # Blanco
            ethnicity_concept_id=38003564,  # No hispano
            location_id=1,
            provider_id=1,
            care_site_id=1,
            person_source_value="PT002"
        )
        
        session.add_all([person1, person2])
        session.flush()
        
        # Crear visita para persona1
        visit1 = VisitOccurrence(
            visit_occurrence_id=1,
            person_id=1,
            visit_concept_id=9202,  # Visita ambulatoria
            visit_start_date=datetime.date(2023, 1, 15),
            visit_start_datetime=datetime.datetime(2023, 1, 15, 9, 30),
            visit_end_date=datetime.date(2023, 1, 15),
            visit_end_datetime=datetime.datetime(2023, 1, 15, 10, 15),
            visit_type_concept_id=32817,  # Registro de EHR
            provider_id=1,
            care_site_id=1
        )
        session.add(visit1)
        
        # Crear visita para persona2
        visit2 = VisitOccurrence(
            visit_occurrence_id=2,
            person_id=2,
            visit_concept_id=9202,  # Visita ambulatoria
            visit_start_date=datetime.date(2023, 2, 3),
            visit_start_datetime=datetime.datetime(2023, 2, 3, 14, 0),
            visit_end_date=datetime.date(2023, 2, 3),
            visit_end_datetime=datetime.datetime(2023, 2, 3, 14, 45),
            visit_type_concept_id=32817,  # Registro de EHR
            provider_id=1,
            care_site_id=1
        )
        session.add(visit2)
        session.flush()
        
        # Crear condiciones
        condition1 = ConditionOccurrence(
            condition_occurrence_id=1,
            person_id=1,
            condition_concept_id=201826,  # Diabetes tipo 2
            condition_start_date=datetime.date(2023, 1, 15),
            condition_start_datetime=datetime.datetime(2023, 1, 15, 9, 45),
            condition_type_concept_id=32817,  # Registro de EHR
            provider_id=1,
            visit_occurrence_id=1
        )
        
        condition2 = ConditionOccurrence(
            condition_occurrence_id=2,
            person_id=1,
            condition_concept_id=320128,  # Hipertensión esencial
            condition_start_date=datetime.date(2023, 1, 15),
            condition_start_datetime=datetime.datetime(2023, 1, 15, 9, 50),
            condition_type_concept_id=32817,  # Registro de EHR
            provider_id=1,
            visit_occurrence_id=1
        )
        
        session.add_all([condition1, condition2])
        session.flush()
        
        # Crear mediciones
        measurement1 = Measurement(
            measurement_id=1,
            person_id=1,
            measurement_concept_id=3004501,  # Glucosa en sangre
            measurement_date=datetime.date(2023, 1, 15),
            measurement_datetime=datetime.datetime(2023, 1, 15, 9, 40),
            measurement_type_concept_id=32817,  # Registro de EHR
            value_as_number=126,  # mg/dL
            unit_concept_id=8840,  # mg/dL
            provider_id=1,
            visit_occurrence_id=1
        )
        
        measurement2 = Measurement(
            measurement_id=2,
            person_id=1,
            measurement_concept_id=3004249,  # Presión arterial
            measurement_date=datetime.date(2023, 1, 15),
            measurement_datetime=datetime.datetime(2023, 1, 15, 9, 35),
            measurement_type_concept_id=32817,  # Registro de EHR
            value_as_string="140/90",
            provider_id=1,
            visit_occurrence_id=1
        )
        
        session.add_all([measurement1, measurement2])
        session.flush()
        
        # Crear medicamentos
        drug1 = DrugExposure(
            drug_exposure_id=1,
            person_id=1,
            drug_concept_id=1503297,  # Metformina
            drug_exposure_start_date=datetime.date(2023, 1, 15),
            drug_exposure_start_datetime=datetime.datetime(2023, 1, 15, 10, 0),
            drug_exposure_end_date=datetime.date(2023, 4, 15),  # 3 meses de tratamiento
            drug_type_concept_id=32817,  # Registro de EHR
            quantity=90,  # 90 tabletas
            days_supply=90,  # 90 días de suministro
            provider_id=1,
            visit_occurrence_id=1
        )
        
        drug2 = DrugExposure(
            drug_exposure_id=2,
            person_id=1,
            drug_concept_id=1308216,  # Lisinopril
            drug_exposure_start_date=datetime.date(2023, 1, 15),
            drug_exposure_start_datetime=datetime.datetime(2023, 1, 15, 10, 0),
            drug_exposure_end_date=datetime.date(2023, 4, 15),  # 3 meses de tratamiento
            drug_type_concept_id=32817,  # Registro de EHR
            quantity=90,  # 90 tabletas
            days_supply=90,  # 90 días de suministro
            provider_id=1,
            visit_occurrence_id=1
        )
        
        session.add_all([drug1, drug2])
        
        # Guardar todos los cambios
        session.commit()
        session.close()
        
        print("Registros de persona de ejemplo creados con éxito.")
    else:
        print("Ya existen registros de persona. Omitiendo creación de registros de ejemplo.")

if __name__ == "__main__":
    initialize_database()
    create_essential_concept_records()
    create_sample_person()
    
    print("Base de datos OMOP-CDM inicializada y datos de ejemplo cargados correctamente.")

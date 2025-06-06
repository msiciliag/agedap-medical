"""
Modelos SQLAlchemy para las tablas de datos clínicos del esquema OMOP-CDM.
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Float, Boolean, Numeric
from sqlalchemy.orm import relationship
from ..database import Base

class Person(Base):
    """
    La tabla PERSON contiene registros que identifican de manera única a cada persona o paciente
    en el sistema de atención médica.
    """
    __tablename__ = "person"
    
    person_id = Column(Integer, primary_key=True)
    gender_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    year_of_birth = Column(Integer, nullable=False)
    month_of_birth = Column(Integer)
    day_of_birth = Column(Integer)
    birth_datetime = Column(DateTime)
    race_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    ethnicity_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    location_id = Column(Integer, ForeignKey("location.location_id"))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    care_site_id = Column(Integer, ForeignKey("care_site.care_site_id"))
    person_source_value = Column(String(50))
    gender_source_value = Column(String(50))
    gender_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    race_source_value = Column(String(50))
    race_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    ethnicity_source_value = Column(String(50))
    ethnicity_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    
    # Relaciones
    gender_concept = relationship("Concept", foreign_keys=[gender_concept_id])
    race_concept = relationship("Concept", foreign_keys=[race_concept_id])
    ethnicity_concept = relationship("Concept", foreign_keys=[ethnicity_concept_id])
    location = relationship("Location")
    provider = relationship("Provider")
    care_site = relationship("CareSite")
    gender_source_concept = relationship("Concept", foreign_keys=[gender_source_concept_id])
    race_source_concept = relationship("Concept", foreign_keys=[race_source_concept_id])
    ethnicity_source_concept = relationship("Concept", foreign_keys=[ethnicity_source_concept_id])
    
    # Relaciones inversas para facilitar el acceso a datos relacionados con la persona
    condition_occurrences = relationship("ConditionOccurrence", back_populates="person")
    drug_exposures = relationship("DrugExposure", back_populates="person")
    measurement_records = relationship("Measurement", back_populates="person")
    observation_records = relationship("Observation", back_populates="person")
    procedure_occurrences = relationship("ProcedureOccurrence", back_populates="person")
    visit_occurrences = relationship("VisitOccurrence", back_populates="person")
    device_exposures = relationship("DeviceExposure", back_populates="person")
    observation_periods = relationship("ObservationPeriod", back_populates="person")
    death_record = relationship("Death", uselist=False, back_populates="person")


class Death(Base):
    """
    La tabla DEATH contiene la fecha y causa de muerte de una persona.
    """
    __tablename__ = "death"
    
    person_id = Column(Integer, ForeignKey("person.person_id"), primary_key=True)
    death_date = Column(Date, nullable=False)
    death_datetime = Column(DateTime)
    death_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    cause_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    cause_source_value = Column(String(50))
    cause_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    
    # Relaciones
    person = relationship("Person", back_populates="death_record")
    death_type_concept = relationship("Concept", foreign_keys=[death_type_concept_id])
    cause_concept = relationship("Concept", foreign_keys=[cause_concept_id])
    cause_source_concept = relationship("Concept", foreign_keys=[cause_source_concept_id])


class VisitOccurrence(Base):
    """
    La tabla VISIT_OCCURRENCE contiene eventos en los que las personas interactúan 
    con el sistema de atención médica durante un período de tiempo.
    """
    __tablename__ = "visit_occurrence"
    
    visit_occurrence_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    visit_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    visit_start_date = Column(Date, nullable=False)
    visit_start_datetime = Column(DateTime)
    visit_end_date = Column(Date, nullable=False)
    visit_end_datetime = Column(DateTime)
    visit_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    care_site_id = Column(Integer, ForeignKey("care_site.care_site_id"))
    visit_source_value = Column(String(50))
    visit_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    admitted_from_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    admitted_from_source_value = Column(String(50))
    discharged_to_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    discharged_to_source_value = Column(String(50))
    preceding_visit_occurrence_id = Column(Integer, ForeignKey("visit_occurrence.visit_occurrence_id"))
    
    # Relaciones
    person = relationship("Person", back_populates="visit_occurrences")
    visit_concept = relationship("Concept", foreign_keys=[visit_concept_id])
    visit_type_concept = relationship("Concept", foreign_keys=[visit_type_concept_id])
    provider = relationship("Provider")
    care_site = relationship("CareSite")
    visit_source_concept = relationship("Concept", foreign_keys=[visit_source_concept_id])
    admitted_from_concept = relationship("Concept", foreign_keys=[admitted_from_concept_id])
    discharged_to_concept = relationship("Concept", foreign_keys=[discharged_to_concept_id])
    preceding_visit = relationship("VisitOccurrence", remote_side=[visit_occurrence_id])
    
    # Relaciones inversas
    condition_occurrences = relationship("ConditionOccurrence", back_populates="visit_occurrence")
    drug_exposures = relationship("DrugExposure", back_populates="visit_occurrence")
    procedure_occurrences = relationship("ProcedureOccurrence", back_populates="visit_occurrence")
    measurement_records = relationship("Measurement", back_populates="visit_occurrence")
    observation_records = relationship("Observation", back_populates="visit_occurrence")
    device_exposures = relationship("DeviceExposure", back_populates="visit_occurrence")
    visit_details = relationship("VisitDetail", back_populates="visit_occurrence")


class VisitDetail(Base):
    """
    La tabla VISIT_DETAIL es una tabla opcional que se utiliza para representar detalles 
    de cada registro en la tabla VISIT_OCCURRENCE.
    """
    __tablename__ = "visit_detail"
    
    visit_detail_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    visit_detail_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    visit_detail_start_date = Column(Date, nullable=False)
    visit_detail_start_datetime = Column(DateTime)
    visit_detail_end_date = Column(Date, nullable=False)
    visit_detail_end_datetime = Column(DateTime)
    visit_detail_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    care_site_id = Column(Integer, ForeignKey("care_site.care_site_id"))
    visit_detail_source_value = Column(String(50))
    visit_detail_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    admitted_from_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    admitted_from_source_value = Column(String(50))
    discharged_to_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    discharged_to_source_value = Column(String(50))
    preceding_visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    parent_visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    visit_occurrence_id = Column(Integer, ForeignKey("visit_occurrence.visit_occurrence_id"), nullable=False)
    
    # Relaciones
    person = relationship("Person")
    visit_detail_concept = relationship("Concept", foreign_keys=[visit_detail_concept_id])
    visit_detail_type_concept = relationship("Concept", foreign_keys=[visit_detail_type_concept_id])
    provider = relationship("Provider")
    care_site = relationship("CareSite")
    visit_detail_source_concept = relationship("Concept", foreign_keys=[visit_detail_source_concept_id])
    admitted_from_concept = relationship("Concept", foreign_keys=[admitted_from_concept_id])
    discharged_to_concept = relationship("Concept", foreign_keys=[discharged_to_concept_id])
    preceding_visit_detail = relationship("VisitDetail", foreign_keys=[preceding_visit_detail_id], remote_side=[visit_detail_id])
    parent_visit_detail = relationship("VisitDetail", foreign_keys=[parent_visit_detail_id], remote_side=[visit_detail_id])
    visit_occurrence = relationship("VisitOccurrence", back_populates="visit_details")


class ConditionOccurrence(Base):
    """
    La tabla CONDITION_OCCURRENCE contiene registros de diagnósticos o condiciones 
    de una persona.
    """
    __tablename__ = "condition_occurrence"
    
    condition_occurrence_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    condition_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    condition_start_date = Column(Date, nullable=False)
    condition_start_datetime = Column(DateTime)
    condition_end_date = Column(Date)
    condition_end_datetime = Column(DateTime)
    condition_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    stop_reason = Column(String(20))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    visit_occurrence_id = Column(Integer, ForeignKey("visit_occurrence.visit_occurrence_id"))
    visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    condition_source_value = Column(String(50))
    condition_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    condition_status_source_value = Column(String(50))
    condition_status_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    
    # Relaciones
    person = relationship("Person", back_populates="condition_occurrences")
    condition_concept = relationship("Concept", foreign_keys=[condition_concept_id])
    condition_type_concept = relationship("Concept", foreign_keys=[condition_type_concept_id])
    provider = relationship("Provider")
    visit_occurrence = relationship("VisitOccurrence", back_populates="condition_occurrences")
    visit_detail = relationship("VisitDetail")
    condition_source_concept = relationship("Concept", foreign_keys=[condition_source_concept_id])
    condition_status_concept = relationship("Concept", foreign_keys=[condition_status_concept_id])


class ProcedureOccurrence(Base):
    """
    La tabla PROCEDURE_OCCURRENCE contiene registros de actividades o procesos 
    ordenados o realizados a una persona.
    """
    __tablename__ = "procedure_occurrence"
    
    procedure_occurrence_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    procedure_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    procedure_date = Column(Date, nullable=False)
    procedure_datetime = Column(DateTime)
    procedure_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    modifier_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    quantity = Column(Integer)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    visit_occurrence_id = Column(Integer, ForeignKey("visit_occurrence.visit_occurrence_id"))
    visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    procedure_source_value = Column(String(50))
    procedure_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    modifier_source_value = Column(String(50))
    
    # Relaciones
    person = relationship("Person", back_populates="procedure_occurrences")
    procedure_concept = relationship("Concept", foreign_keys=[procedure_concept_id])
    procedure_type_concept = relationship("Concept", foreign_keys=[procedure_type_concept_id])
    modifier_concept = relationship("Concept", foreign_keys=[modifier_concept_id])
    provider = relationship("Provider")
    visit_occurrence = relationship("VisitOccurrence", back_populates="procedure_occurrences")
    visit_detail = relationship("VisitDetail")
    procedure_source_concept = relationship("Concept", foreign_keys=[procedure_source_concept_id])


class DrugExposure(Base):
    """
    La tabla DRUG_EXPOSURE contiene registros de exposición a una sustancia 
    que se administra a una persona.
    """
    __tablename__ = "drug_exposure"
    
    drug_exposure_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    drug_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    drug_exposure_start_date = Column(Date, nullable=False)
    drug_exposure_start_datetime = Column(DateTime)
    drug_exposure_end_date = Column(Date, nullable=False)
    drug_exposure_end_datetime = Column(DateTime)
    verbatim_end_date = Column(Date)
    drug_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    stop_reason = Column(String(20))
    refills = Column(Integer)
    quantity = Column(Numeric)
    days_supply = Column(Integer)
    sig = Column(Text)
    route_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    lot_number = Column(String(50))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    visit_occurrence_id = Column(Integer, ForeignKey("visit_occurrence.visit_occurrence_id"))
    visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    drug_source_value = Column(String(50))
    drug_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    route_source_value = Column(String(50))
    dose_unit_source_value = Column(String(50))
    
    # Relaciones
    person = relationship("Person", back_populates="drug_exposures")
    drug_concept = relationship("Concept", foreign_keys=[drug_concept_id])
    drug_type_concept = relationship("Concept", foreign_keys=[drug_type_concept_id])
    route_concept = relationship("Concept", foreign_keys=[route_concept_id])
    provider = relationship("Provider")
    visit_occurrence = relationship("VisitOccurrence", back_populates="drug_exposures")
    visit_detail = relationship("VisitDetail")
    drug_source_concept = relationship("Concept", foreign_keys=[drug_source_concept_id])


class DeviceExposure(Base):
    """
    La tabla DEVICE_EXPOSURE contiene registros de exposición a un dispositivo 
    que se administra a una persona.
    """
    __tablename__ = "device_exposure"
    
    device_exposure_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    device_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    device_exposure_start_date = Column(Date, nullable=False)
    device_exposure_start_datetime = Column(DateTime)
    device_exposure_end_date = Column(Date)
    device_exposure_end_datetime = Column(DateTime)
    device_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    unique_device_id = Column(String(50))
    quantity = Column(Integer)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    visit_occurrence_id = Column(Integer, ForeignKey("visit_occurrence.visit_occurrence_id"))
    visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    device_source_value = Column(String(100))
    device_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    
    # Relaciones
    person = relationship("Person", back_populates="device_exposures")
    device_concept = relationship("Concept", foreign_keys=[device_concept_id])
    device_type_concept = relationship("Concept", foreign_keys=[device_type_concept_id])
    provider = relationship("Provider")
    visit_occurrence = relationship("VisitOccurrence", back_populates="device_exposures")
    visit_detail = relationship("VisitDetail")
    device_source_concept = relationship("Concept", foreign_keys=[device_source_concept_id])


class Measurement(Base):
    """
    La tabla MEASUREMENT contiene registros de mediciones realizadas a una persona.
    """
    __tablename__ = "measurement"
    
    measurement_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    measurement_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    measurement_date = Column(Date, nullable=False)
    measurement_datetime = Column(DateTime)
    measurement_time = Column(String(10))
    measurement_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    operator_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    value_as_number = Column(Numeric)
    value_as_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    unit_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    range_low = Column(Numeric)
    range_high = Column(Numeric)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    visit_occurrence_id = Column(Integer, ForeignKey("visit_occurrence.visit_occurrence_id"))
    visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    measurement_source_value = Column(String(50))
    measurement_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    unit_source_value = Column(String(50))
    value_source_value = Column(String(50))
    
    # Relaciones
    person = relationship("Person", back_populates="measurement_records")
    measurement_concept = relationship("Concept", foreign_keys=[measurement_concept_id])
    measurement_type_concept = relationship("Concept", foreign_keys=[measurement_type_concept_id])
    operator_concept = relationship("Concept", foreign_keys=[operator_concept_id])
    value_as_concept = relationship("Concept", foreign_keys=[value_as_concept_id])
    unit_concept = relationship("Concept", foreign_keys=[unit_concept_id])
    provider = relationship("Provider")
    visit_occurrence = relationship("VisitOccurrence", back_populates="measurement_records")
    visit_detail = relationship("VisitDetail")
    measurement_source_concept = relationship("Concept", foreign_keys=[measurement_source_concept_id])


class Observation(Base):
    """
    La tabla OBSERVATION contiene registros de estados clínicos de una persona 
    que no se capturan en otras tablas.
    """
    __tablename__ = "observation"
    
    observation_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    observation_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    observation_date = Column(Date, nullable=False)
    observation_datetime = Column(DateTime)
    observation_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    value_as_number = Column(Numeric)
    value_as_string = Column(String(60))
    value_as_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    qualifier_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    unit_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    visit_occurrence_id = Column(Integer, ForeignKey("visit_occurrence.visit_occurrence_id"))
    visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    observation_source_value = Column(String(50))
    observation_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    unit_source_value = Column(String(50))
    qualifier_source_value = Column(String(50))
    
    # Relaciones
    person = relationship("Person", back_populates="observation_records")
    observation_concept = relationship("Concept", foreign_keys=[observation_concept_id])
    observation_type_concept = relationship("Concept", foreign_keys=[observation_type_concept_id])
    value_as_concept = relationship("Concept", foreign_keys=[value_as_concept_id])
    qualifier_concept = relationship("Concept", foreign_keys=[qualifier_concept_id])
    unit_concept = relationship("Concept", foreign_keys=[unit_concept_id])
    provider = relationship("Provider")
    visit_occurrence = relationship("VisitOccurrence", back_populates="observation_records")
    visit_detail = relationship("VisitDetail")
    observation_source_concept = relationship("Concept", foreign_keys=[observation_source_concept_id])


class Note(Base):
    """
    La tabla NOTE contiene información no estructurada registrada por un proveedor 
    sobre una persona en texto libre en una fecha determinada.
    """
    __tablename__ = "note"
    
    note_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    note_date = Column(Date, nullable=False)
    note_datetime = Column(DateTime)
    note_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    note_class_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    note_title = Column(String(250))
    note_text = Column(Text, nullable=False)
    encoding_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    language_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    visit_occurrence_id = Column(Integer, ForeignKey("visit_occurrence.visit_occurrence_id"))
    visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    note_source_value = Column(String(50))
    
    # Relaciones
    person = relationship("Person")
    note_type_concept = relationship("Concept", foreign_keys=[note_type_concept_id])
    note_class_concept = relationship("Concept", foreign_keys=[note_class_concept_id])
    encoding_concept = relationship("Concept", foreign_keys=[encoding_concept_id])
    language_concept = relationship("Concept", foreign_keys=[language_concept_id])
    provider = relationship("Provider")
    visit_occurrence = relationship("VisitOccurrence")
    visit_detail = relationship("VisitDetail")
    note_nlp_records = relationship("NoteNlp", back_populates="note")


class NoteNlp(Base):
    """
    La tabla NOTE_NLP codifica todos los resultados del procesamiento del lenguaje natural (NLP) 
    en notas clínicas. Cada fila representa un único término extraído de una nota.
    """
    __tablename__ = "note_nlp"
    
    note_nlp_id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey("note.note_id"), nullable=False)
    section_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    snippet = Column(String(250))
    offset = Column(String(50))
    lexical_variant = Column(String(250), nullable=False)
    note_nlp_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    note_nlp_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    nlp_system = Column(String(250))
    nlp_date = Column(Date, nullable=False)
    nlp_datetime = Column(DateTime)
    term_exists = Column(String(1))
    term_temporal = Column(String(50))
    term_modifiers = Column(String(2000))
    
    # Relaciones
    note = relationship("Note", back_populates="note_nlp_records")
    section_concept = relationship("Concept", foreign_keys=[section_concept_id])
    note_nlp_concept = relationship("Concept", foreign_keys=[note_nlp_concept_id])
    note_nlp_source_concept = relationship("Concept", foreign_keys=[note_nlp_source_concept_id])


class Specimen(Base):
    """
    La tabla SPECIMEN contiene información sobre muestras biológicas de una persona.
    """
    __tablename__ = "specimen"
    
    specimen_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    specimen_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    specimen_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    specimen_date = Column(Date, nullable=False)
    specimen_datetime = Column(DateTime)
    quantity = Column(Numeric)
    unit_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    anatomic_site_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    disease_status_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    specimen_source_id = Column(String(50))
    specimen_source_value = Column(String(50))
    unit_source_value = Column(String(50))
    anatomic_site_source_value = Column(String(50))
    disease_status_source_value = Column(String(50))
    
    # Relaciones
    person = relationship("Person")
    specimen_concept = relationship("Concept", foreign_keys=[specimen_concept_id])
    specimen_type_concept = relationship("Concept", foreign_keys=[specimen_type_concept_id])
    unit_concept = relationship("Concept", foreign_keys=[unit_concept_id])
    anatomic_site_concept = relationship("Concept", foreign_keys=[anatomic_site_concept_id])
    disease_status_concept = relationship("Concept", foreign_keys=[disease_status_concept_id])


class ObservationPeriod(Base):
    """
    La tabla OBSERVATION_PERIOD contiene registros de períodos continuos de cobertura 
    de observación de una persona.
    """
    __tablename__ = "observation_period"
    
    observation_period_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    observation_period_start_date = Column(Date, nullable=False)
    observation_period_end_date = Column(Date, nullable=False)
    period_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    
    # Relaciones
    person = relationship("Person", back_populates="observation_periods")
    period_type_concept = relationship("Concept", foreign_keys=[period_type_concept_id])

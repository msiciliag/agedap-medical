"""
Modelos SQLAlchemy para las tablas de elementos derivados del esquema OMOP-CDM.
"""
import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ConditionEra(Base):
    """
    La tabla CONDITION_ERA agrega registros de la tabla CONDITION_OCCURRENCE
    en períodos continuos de una condición específica.
    """
    __tablename__ = "condition_era"
    
    condition_era_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    condition_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    condition_era_start_date = Column(Date, nullable=False)
    condition_era_end_date = Column(Date, nullable=False)
    condition_occurrence_count = Column(Integer)
    
    # Relaciones
    person = relationship("Person")
    condition_concept = relationship("Concept", foreign_keys=[condition_concept_id])


class DrugEra(Base):
    """
    La tabla DRUG_ERA agrega registros de la tabla DRUG_EXPOSURE
    en períodos continuos de exposición a un medicamento.
    """
    __tablename__ = "drug_era"
    
    drug_era_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    drug_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    drug_era_start_date = Column(Date, nullable=False)
    drug_era_end_date = Column(Date, nullable=False)
    drug_exposure_count = Column(Integer)
    gap_days = Column(Integer)
    
    # Relaciones
    person = relationship("Person")
    drug_concept = relationship("Concept", foreign_keys=[drug_concept_id])


class DoseEra(Base):
    """
    La tabla DOSE_ERA agrega registros de la tabla DRUG_EXPOSURE
    en períodos continuos de exposición a un medicamento con dosis consistente.
    """
    __tablename__ = "dose_era"
    
    dose_era_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    drug_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    unit_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    dose_value = Column(Integer, nullable=False)
    dose_era_start_date = Column(Date, nullable=False)
    dose_era_end_date = Column(Date, nullable=False)
    
    # Relaciones
    person = relationship("Person")
    drug_concept = relationship("Concept", foreign_keys=[drug_concept_id])
    unit_concept = relationship("Concept", foreign_keys=[unit_concept_id])


class Episode(Base):
    """
    La tabla EPISODE agrega eventos clínicos de nivel inferior en una abstracción 
    de nivel superior que representa fases de enfermedades, resultados y tratamientos.
    """
    __tablename__ = "episode"
    
    episode_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    episode_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    episode_start_date = Column(Date, nullable=False)
    episode_start_datetime = Column(DateTime)
    episode_end_date = Column(Date)
    episode_end_datetime = Column(DateTime)
    episode_parent_id = Column(Integer, ForeignKey("episode.episode_id"))
    episode_number = Column(Integer)
    episode_object_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    episode_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    episode_source_value = Column(String(50))
    episode_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    
    # Relaciones
    person = relationship("Person")
    episode_concept = relationship("Concept", foreign_keys=[episode_concept_id])
    episode_parent = relationship("Episode", remote_side=[episode_id], backref="episode_children")
    episode_object_concept = relationship("Concept", foreign_keys=[episode_object_concept_id])
    episode_type_concept = relationship("Concept", foreign_keys=[episode_type_concept_id])
    episode_source_concept = relationship("Concept", foreign_keys=[episode_source_concept_id])
    
    # Relaciones inversas
    episode_events = relationship("EpisodeEvent", back_populates="episode")


class EpisodeEvent(Base):
    """
    La tabla EPISODE_EVENT conecta eventos clínicos calificados con la entrada 
    EPISODE apropiada.
    """
    __tablename__ = "episode_event"
    
    episode_id = Column(Integer, ForeignKey("episode.episode_id"), primary_key=True)
    event_id = Column(Integer, primary_key=True)
    episode_event_field_concept_id = Column(Integer, ForeignKey("concept.concept_id"), primary_key=True)
    
    # Relaciones
    episode = relationship("Episode", back_populates="episode_events")
    episode_event_field_concept = relationship("Concept", foreign_keys=[episode_event_field_concept_id])

"""
Modelos SQLAlchemy para las tablas de metadatos del esquema OMOP-CDM.
"""
import datetime
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from ..database import Base

class Metadata(Base):
    """
    La tabla METADATA contiene información de metadatos sobre un conjunto de datos 
    transformado al modelo OMOP-CDM.
    """
    __tablename__ = "metadata"
    
    metadata_id = Column(Integer, primary_key=True)
    metadata_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    metadata_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    name = Column(String(250), nullable=False)
    value_as_string = Column(String(250))
    value_as_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    value_as_number = Column(Numeric)
    metadata_date = Column(Date)
    metadata_datetime = Column(Date) # En OMOP-CDM v5.4 es DATETIME, no Date. Considerar cambiar a DateTime.
    
    # Relaciones
    metadata_concept = relationship("Concept", foreign_keys=[metadata_concept_id])
    metadata_type_concept = relationship("Concept", foreign_keys=[metadata_type_concept_id])
    value_as_concept = relationship("Concept", foreign_keys=[value_as_concept_id])


class CdmSource(Base):
    """
    La tabla CDM_SOURCE contiene detalles sobre la base de datos de origen y
    el proceso utilizado para transformar los datos al modelo OMOP-CDM.
    """
    __tablename__ = "cdm_source"
    
    # Se usa cdm_source_name como identificador principal en lugar de un id numérico.
    # OMOP CDM v5.4 no define explícitamente una clave primaria única para esta tabla, 
    # pero una combinación de campos como cdm_source_name, cdm_version, y vocabulary_version
    # podría considerarse una clave compuesta en la práctica, aunque SQLAlchemy requiere una PK.
    # Para simplificar, y dado que el usuario ya lo tenía así, mantendremos las PK definidas.
    # Sin embargo, es importante notar que el estándar OMOP no siempre define PKs explicitas.
    
    cdm_source_name = Column(String(255), nullable=False, primary_key=True)
    cdm_source_abbreviation = Column(String(25), nullable=False, primary_key=True)
    cdm_holder = Column(String(255), nullable=False, primary_key=True)
    source_description = Column(Text)
    source_documentation_reference = Column(String(255))
    cdm_etl_reference = Column(String(255))
    source_release_date = Column(Date, nullable=False, primary_key=True)
    cdm_release_date = Column(Date, nullable=False, primary_key=True)
    cdm_version = Column(String(10)) # OMOP define VARCHAR(10)
    cdm_version_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False, primary_key=True)
    vocabulary_version = Column(String(20), nullable=False, primary_key=True)
    
    # Relaciones
    cdm_version_concept = relationship("Concept", foreign_keys=[cdm_version_concept_id])

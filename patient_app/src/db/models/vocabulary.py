"""
Modelos SQLAlchemy para las tablas de vocabulario del esquema OMOP-CDM.
"""
import datetime
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Concept(Base):
    """
    La tabla CONCEPT contiene conceptos estandarizados que conforman el vocabulario OMOP-CDM.
    """
    __tablename__ = "concept"
    
    concept_id = Column(Integer, primary_key=True)
    concept_name = Column(String(255), nullable=False)
    domain_id = Column(String(20), ForeignKey("domain.domain_id"), nullable=False)
    vocabulary_id = Column(String(20), ForeignKey("vocabulary.vocabulary_id"), nullable=False)
    concept_class_id = Column(String(20), ForeignKey("concept_class.concept_class_id"), nullable=False)
    standard_concept = Column(String(1))
    concept_code = Column(String(50), nullable=False)
    valid_start_date = Column(Date, nullable=False)
    valid_end_date = Column(Date, nullable=False)
    invalid_reason = Column(String(1))
    
    # Relaciones
    domain = relationship("Domain")
    vocabulary = relationship("Vocabulary")
    concept_class = relationship("ConceptClass")


class Vocabulary(Base):
    """
    La tabla VOCABULARY contiene vocabularios de terminología médica utilizados 
    en el modelo OMOP-CDM.
    """
    __tablename__ = "vocabulary"
    
    vocabulary_id = Column(String(20), primary_key=True)
    vocabulary_name = Column(String(255), nullable=False)
    vocabulary_reference = Column(String(255))
    vocabulary_version = Column(String(255))
    vocabulary_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    
    # Relaciones
    vocabulary_concept = relationship("Concept", foreign_keys=[vocabulary_concept_id])


class Domain(Base):
    """
    La tabla DOMAIN contiene los dominios en los que se pueden clasificar los conceptos.
    """
    __tablename__ = "domain"
    
    domain_id = Column(String(20), primary_key=True)
    domain_name = Column(String(255), nullable=False)
    domain_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    
    # Relaciones
    domain_concept = relationship("Concept", foreign_keys=[domain_concept_id])


class ConceptClass(Base):
    """
    La tabla CONCEPT_CLASS contiene las clases en las que se pueden clasificar los conceptos.
    """
    __tablename__ = "concept_class"
    
    concept_class_id = Column(String(20), primary_key=True)
    concept_class_name = Column(String(255), nullable=False)
    concept_class_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    
    # Relaciones
    concept_class_concept = relationship("Concept", foreign_keys=[concept_class_concept_id])


class ConceptRelationship(Base):
    """
    La tabla CONCEPT_RELATIONSHIP define relaciones entre conceptos.
    """
    __tablename__ = "concept_relationship"
    
    concept_id_1 = Column(Integer, ForeignKey("concept.concept_id"), primary_key=True)
    concept_id_2 = Column(Integer, ForeignKey("concept.concept_id"), primary_key=True)
    relationship_id = Column(String(20), ForeignKey("relationship.relationship_id"), primary_key=True)
    valid_start_date = Column(Date, nullable=False)
    valid_end_date = Column(Date, nullable=False)
    invalid_reason = Column(String(1))
    
    # Relaciones
    concept_1 = relationship("Concept", foreign_keys=[concept_id_1])
    concept_2 = relationship("Concept", foreign_keys=[concept_id_2])
    relationship = relationship("Relationship")


class ConceptAncestor(Base):
    """
    La tabla CONCEPT_ANCESTOR contiene las relaciones ancestrales entre conceptos.
    """
    __tablename__ = "concept_ancestor"
    
    ancestor_concept_id = Column(Integer, ForeignKey("concept.concept_id"), primary_key=True)
    descendant_concept_id = Column(Integer, ForeignKey("concept.concept_id"), primary_key=True)
    min_levels_of_separation = Column(Integer, nullable=False)
    max_levels_of_separation = Column(Integer, nullable=False)
    
    # Relaciones
    ancestor_concept = relationship("Concept", foreign_keys=[ancestor_concept_id])
    descendant_concept = relationship("Concept", foreign_keys=[descendant_concept_id])


class ConceptSynonym(Base):
    """
    La tabla CONCEPT_SYNONYM contiene sinónimos alternativos para conceptos estándar.
    """
    __tablename__ = "concept_synonym"
    
    concept_id = Column(Integer, ForeignKey("concept.concept_id"), primary_key=True)
    concept_synonym_name = Column(String(1000), primary_key=True)
    language_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    
    # Relaciones
    concept = relationship("Concept", foreign_keys=[concept_id])
    language_concept = relationship("Concept", foreign_keys=[language_concept_id])


class Relationship(Base):
    """
    La tabla RELATIONSHIP define los tipos de relación entre conceptos.
    """
    __tablename__ = "relationship"
    
    relationship_id = Column(String(20), primary_key=True)
    relationship_name = Column(String(255), nullable=False)
    is_hierarchical = Column(String(1), nullable=False)
    defines_ancestry = Column(String(1), nullable=False)
    reverse_relationship_id = Column(String(20), ForeignKey("relationship.relationship_id"))
    relationship_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    
    # Relaciones
    reverse_relationship = relationship("Relationship", remote_side=[relationship_id])
    relationship_concept = relationship("Concept", foreign_keys=[relationship_concept_id])


class SourceToConceptMap(Base):
    """
    La tabla SOURCE_TO_CONCEPT_MAP contiene las asignaciones entre códigos de origen y conceptos estándar.
    """
    __tablename__ = "source_to_concept_map"
    
    source_code = Column(String(1000), primary_key=True)
    source_concept_id = Column(Integer, ForeignKey("concept.concept_id"), primary_key=True)
    source_vocabulary_id = Column(String(20), ForeignKey("vocabulary.vocabulary_id"), primary_key=True)
    source_code_description = Column(String(255))
    target_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    target_vocabulary_id = Column(String(20), ForeignKey("vocabulary.vocabulary_id"), nullable=False)
    valid_start_date = Column(Date, nullable=False)
    valid_end_date = Column(Date, nullable=False)
    invalid_reason = Column(String(1))
    
    # Relaciones
    source_concept = relationship("Concept", foreign_keys=[source_concept_id])
    source_vocabulary = relationship("Vocabulary", foreign_keys=[source_vocabulary_id])
    target_concept = relationship("Concept", foreign_keys=[target_concept_id])
    target_vocabulary = relationship("Vocabulary", foreign_keys=[target_vocabulary_id])


class DrugStrength(Base):
    """
    La tabla DRUG_STRENGTH contiene información sobre la cantidad o concentración 
    de un ingrediente específico contenido en un producto farmacéutico.
    """
    __tablename__ = "drug_strength"
    
    drug_concept_id = Column(Integer, ForeignKey("concept.concept_id"), primary_key=True)
    ingredient_concept_id = Column(Integer, ForeignKey("concept.concept_id"), primary_key=True)
    amount_value = Column(String(255))
    amount_unit_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    numerator_value = Column(String(255))
    numerator_unit_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    denominator_value = Column(String(255))
    denominator_unit_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    box_size = Column(Integer)
    valid_start_date = Column(Date, nullable=False, primary_key=True)
    valid_end_date = Column(Date, nullable=False, primary_key=True)
    invalid_reason = Column(String(1))
    
    # Relaciones
    drug_concept = relationship("Concept", foreign_keys=[drug_concept_id])
    ingredient_concept = relationship("Concept", foreign_keys=[ingredient_concept_id])
    amount_unit_concept = relationship("Concept", foreign_keys=[amount_unit_concept_id])
    numerator_unit_concept = relationship("Concept", foreign_keys=[numerator_unit_concept_id])
    denominator_unit_concept = relationship("Concept", foreign_keys=[denominator_unit_concept_id])

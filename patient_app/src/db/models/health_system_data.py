"""
Modelos SQLAlchemy para las tablas de datos del sistema de salud del esquema OMOP-CDM.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Location(Base):
    """
    La tabla LOCATION contiene información sobre ubicaciones geográficas 
    donde se brindan servicios de atención médica.
    """
    __tablename__ = "location"
    
    location_id = Column(Integer, primary_key=True)
    address_1 = Column(String(50))
    address_2 = Column(String(50))
    city = Column(String(50))
    state = Column(String(2))
    zip = Column(String(9))
    county = Column(String(20))
    location_source_value = Column(String(50))
    
    # Relaciones inversas
    persons = relationship("Person", back_populates="location")
    care_sites = relationship("CareSite", back_populates="location")


class CareSite(Base):
    """
    La tabla CARE_SITE contiene información sobre los lugares donde se presta 
    atención médica a pacientes.
    """
    __tablename__ = "care_site"
    
    care_site_id = Column(Integer, primary_key=True)
    care_site_name = Column(String(255))
    place_of_service_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    location_id = Column(Integer, ForeignKey("location.location_id"))
    care_site_source_value = Column(String(50))
    place_of_service_source_value = Column(String(50))
    
    # Relaciones
    location = relationship("Location", back_populates="care_sites")
    place_of_service_concept = relationship("Concept", foreign_keys=[place_of_service_concept_id])
    
    # Relaciones inversas
    providers = relationship("Provider", back_populates="care_site")
    persons = relationship("Person", back_populates="care_site")


class Provider(Base):
    """
    La tabla PROVIDER contiene una lista de proveedores de atención médica 
    identificados de manera única.
    """
    __tablename__ = "provider"
    
    provider_id = Column(Integer, primary_key=True)
    provider_name = Column(String(255))
    npi = Column(String(20))
    dea = Column(String(20))
    specialty_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    care_site_id = Column(Integer, ForeignKey("care_site.care_site_id"))
    year_of_birth = Column(Integer)
    gender_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    provider_source_value = Column(String(50))
    specialty_source_value = Column(String(50))
    specialty_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    gender_source_value = Column(String(50))
    gender_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    
    # Relaciones
    care_site = relationship("CareSite", back_populates="providers")
    specialty_concept = relationship("Concept", foreign_keys=[specialty_concept_id])
    gender_concept = relationship("Concept", foreign_keys=[gender_concept_id])
    specialty_source_concept = relationship("Concept", foreign_keys=[specialty_source_concept_id])
    gender_source_concept = relationship("Concept", foreign_keys=[gender_source_concept_id])
    
    # Relaciones inversas
    persons = relationship("Person", back_populates="provider")

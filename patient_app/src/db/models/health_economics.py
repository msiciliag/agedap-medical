"""
Modelos SQLAlchemy para las tablas de economía de la salud del esquema OMOP-CDM.
"""
import datetime
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from ..database import Base

class PayerPlanPeriod(Base):
    """
    La tabla PAYER_PLAN_PERIOD contiene registros de períodos en los que
    una persona está inscrita en un plan de seguro médico.
    """
    __tablename__ = "payer_plan_period"
    
    payer_plan_period_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    payer_plan_period_start_date = Column(Date, nullable=False)
    payer_plan_period_end_date = Column(Date, nullable=False)
    payer_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    payer_source_value = Column(String(50))
    payer_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    plan_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    plan_source_value = Column(String(50))
    plan_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    sponsor_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    sponsor_source_value = Column(String(50))
    sponsor_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    family_source_value = Column(String(50))
    stop_reason_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    stop_reason_source_value = Column(String(50))
    stop_reason_source_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    
    # Relaciones
    person = relationship("Person")
    payer_concept = relationship("Concept", foreign_keys=[payer_concept_id])
    payer_source_concept = relationship("Concept", foreign_keys=[payer_source_concept_id])
    plan_concept = relationship("Concept", foreign_keys=[plan_concept_id])
    plan_source_concept = relationship("Concept", foreign_keys=[plan_source_concept_id])
    sponsor_concept = relationship("Concept", foreign_keys=[sponsor_concept_id])
    sponsor_source_concept = relationship("Concept", foreign_keys=[sponsor_source_concept_id])
    stop_reason_concept = relationship("Concept", foreign_keys=[stop_reason_concept_id])
    stop_reason_source_concept = relationship("Concept", foreign_keys=[stop_reason_source_concept_id])


class Cost(Base):
    """
    La tabla COST contiene registros de la información financiera de los servicios
    de atención médica.
    """
    __tablename__ = "cost"
    
    cost_id = Column(Integer, primary_key=True)
    cost_event_id = Column(Integer, nullable=False)
    cost_domain_id = Column(String(20), ForeignKey("domain.domain_id"), nullable=False)
    cost_type_concept_id = Column(Integer, ForeignKey("concept.concept_id"), nullable=False)
    currency_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    total_charge = Column(Numeric)
    total_cost = Column(Numeric)
    total_paid = Column(Numeric)
    paid_by_payer = Column(Numeric)
    paid_by_patient = Column(Numeric)
    paid_patient_copay = Column(Numeric)
    paid_patient_coinsurance = Column(Numeric)
    paid_patient_deductible = Column(Numeric)
    paid_by_primary = Column(Numeric)
    paid_ingredient_cost = Column(Numeric)
    paid_dispensing_fee = Column(Numeric)
    payer_plan_period_id = Column(Integer, ForeignKey("payer_plan_period.payer_plan_period_id"))
    amount_allowed = Column(Numeric)
    revenue_code_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    revenue_code_source_value = Column(String(50))
    drg_concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    drg_source_value = Column(String(3))
    
    # Relaciones
    cost_domain = relationship("Domain", foreign_keys=[cost_domain_id])
    cost_type_concept = relationship("Concept", foreign_keys=[cost_type_concept_id])
    currency_concept = relationship("Concept", foreign_keys=[currency_concept_id])
    payer_plan_period = relationship("PayerPlanPeriod")
    revenue_code_concept = relationship("Concept", foreign_keys=[revenue_code_concept_id])
    drg_concept = relationship("Concept", foreign_keys=[drg_concept_id])

"""
Modelos SQLAlchemy para el esquema OMOP-CDM.

Este módulo contiene todas las definiciones de tablas según el esquema OMOP-CDM
(Observational Medical Outcomes Partnership Common Data Model) versión 5.4.

Los modelos incluyen las principales tablas clínicas (Person, Visit_Occurrence, etc.)
y las tablas de vocabulario (Concept, Concept_Relationship, etc.).
"""
from .clinical_data import (
    Person,
    Death,
    VisitOccurrence,
    VisitDetail,
    ConditionOccurrence,
    ProcedureOccurrence,
    DrugExposure,
    DeviceExposure,
    Measurement,
    Observation,
    Note,
    NoteNlp,
    Specimen,
    ObservationPeriod
)

from .derived_elements import (
    ConditionEra,
    DoseEra,
    DrugEra,
    Episode,
    EpisodeEvent
)

from .health_system_data import (
    Location,
    CareSite,
    Provider
)

from .health_economics import (
    PayerPlanPeriod,
    Cost
)

from .vocabulary import (
    Concept,
    Vocabulary,
    Domain,
    ConceptClass,
    ConceptRelationship,
    ConceptAncestor,
    ConceptSynonym,
    Relationship,
    SourceToConceptMap,
    DrugStrength
)

from .metadata import (
    Metadata,
    CdmSource
)

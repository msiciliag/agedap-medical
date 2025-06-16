import inspect
import logging 
from db.config import get_session 
from omopmodel import OMOP_5_4_declarative as omop54
import standard_definitions.terminology_definitions as terminology_defs 
import datetime

# Configure logger for this module
logger = logging.getLogger(__name__)

def load_defined_custom_concepts():
    """
    Loads custom OMOP concepts defined in standard_definitions.terminology_definitions.ALL_DEFINITIONS
    into the database if they are not already present.
    """
    logger.info("Loading custom OMOP concepts from ALL_DEFINITIONS...")
    today_date = datetime.date.today()
    concepts_to_add_list = []

    def _prepare_concept_data(concept_id, source_value, domain_id, concept_class_id="Clinical Finding", vocabulary_id="Local", standard_concept="S"):
        domain_id_capitalized = domain_id.title() if domain_id else "Unknown" 
        return {
            "concept_id": concept_id,
            "concept_name": source_value.replace('_', ' ').title(),
            "domain_id": domain_id_capitalized,
            "vocabulary_id": vocabulary_id,
            "concept_class_id": concept_class_id,
            "standard_concept": standard_concept,
            "concept_code": source_value,
            "valid_start_date": today_date,
            "valid_end_date": datetime.date(2099, 12, 31),
            "invalid_reason": None
        }

    with get_session() as session:
        for value_name, definition in terminology_defs.ALL_DEFINITIONS.items():
            concept_id = definition.get("omop_concept_id")
            source_value = definition.get("source_value")
            domain_id = definition.get("domain")

            if not all([concept_id, source_value, domain_id]):
                logger.warning(f"Definition for '{value_name}' is missing omop_concept_id, source_value, or domain. Skipping.")
                continue

            exists = session.query(omop54.Concept.concept_id).filter_by(concept_id=concept_id).scalar() is not None
            if not exists:
                logger.info(f"Preparing to add concept: ID={concept_id}, Name={source_value}, Domain={domain_id}")
                concept_data = _prepare_concept_data(concept_id, source_value, domain_id)
                concepts_to_add_list.append(omop54.Concept(**concept_data))
            else:
                logger.debug(f"Concept ID {concept_id} ({source_value}) already exists. Skipping.")
        
        if concepts_to_add_list:
            try:
                session.add_all(concepts_to_add_list)
                session.commit()
                logger.info(f"Added {len(concepts_to_add_list)} new custom OMOP concepts.")
            except Exception as e:
                logger.error(f"Error committing new concepts to database: {e}")
                session.rollback()
        else:
            logger.info("All custom OMOP concepts from ALL_DEFINITIONS already exist or no new definitions found.")
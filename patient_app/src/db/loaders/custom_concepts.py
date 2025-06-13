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
    Dynamically discovers and inserts custom OMOP concepts defined in 
    standard_definitions.terminology_definitions.py into the database 
    if they are not already present. It expects definition variables to end with '_DEFINITIONS'.
    """
    logger.info("Dynamically checking and loading custom OMOP concepts (expecting '_DEFINITIONS' suffix)...")
    today_date = datetime.date.today()
    concepts_to_add_list = []

    def _prepare_concept_data(concept_id, source_value, domain_id, concept_class_id="Clinical Finding", vocabulary_id="Local", standard_concept="S"):
        return {
            "concept_id": concept_id,
            "concept_name": source_value.replace('_', ' ').title(),
            "domain_id": domain_id,
            "vocabulary_id": vocabulary_id,
            "concept_class_id": concept_class_id,
            "standard_concept": standard_concept,
            "concept_code": source_value,
            "valid_start_date": today_date,
            "valid_end_date": datetime.date(2099, 12, 31),
            "invalid_reason": None
        }

    processed_definitions_prefixes = set()

    with get_session() as session:
        for name, member in inspect.getmembers(terminology_defs):
            if name.startswith("__") or not name.endswith("_DEFINITIONS"):
                continue

            service_prefix = name[:-len("_DEFINITIONS")]

            if service_prefix in processed_definitions_prefixes:
                continue

            definitions_value = member
            start_id_value = None
            
            start_id_name = f"{service_prefix}_CONCEPT_START_ID"
            if hasattr(terminology_defs, start_id_name):
                start_id_value = getattr(terminology_defs, start_id_name)
            else:
                logger.warning(f"Could not find start ID variable {start_id_name} for definitions {name}. Skipping {service_prefix} concepts.")
                continue
            
            logger.info(f"Processing concepts for: {service_prefix.replace('_', ' ').title()}")
            current_id = start_id_value
            
            processed_definitions_prefixes.add(service_prefix)

            if isinstance(definitions_value, dict): # e.g., DIABETES_DEFINITIONS, BREAST_CANCER_DEFINITIONS
                for domain_key, def_list in definitions_value.items():
                    logger.info(f"  Domain: {domain_key.title()}")
                    for item_def in def_list:
                        exists = session.query(omop54.Concept.concept_id).filter_by(concept_id=current_id).scalar() is not None
                        if not exists:
                            concept_data = _prepare_concept_data(current_id, item_def["source_value"], domain_key.title())
                            concepts_to_add_list.append(omop54.Concept(**concept_data))
                        current_id += 1
            else:
                logger.warning(f"Unsupported type for definitions variable {name}: {type(definitions_value)}. Expected dict. Skipping.")
        
        if concepts_to_add_list:
            session.add_all(concepts_to_add_list)
            session.commit()
            logger.info(f"Added {len(concepts_to_add_list)} new custom OMOP concepts.")
        else:
            logger.info("All discovered custom OMOP concepts already exist or no new definitions found.")


from src.app_config import USER_PATIENT_IDS
from pathlib import Path
from src.utils.fhir import _load_bundle_from_file
import logging

logger = logging.getLogger(__name__)

def load_fhir_bundles_from_directory():
    """
    Load all FHIR bundles from the data/fhir_bundles directory.
    """
    current_dir = Path(__file__).parent
    general_bundles_dir = current_dir / "src" / "data" / "fhir_bundles"
    patient_ids = list(USER_PATIENT_IDS.values())
    
    for patient_id in patient_ids:
        bundles_dir = general_bundles_dir / patient_id

        logging.info(f"Looking for FHIR bundles in: {bundles_dir}")

        if not bundles_dir.exists():
            logging.error(f"Error: Directory {bundles_dir} does not exist")
            return []

        loaded_bundles = []

        json_files = list(bundles_dir.glob("*.json"))

        if not json_files:
            logger.error("No JSON files found in the bundles directory")
            return []

        logging.info(f"Found {len(json_files)} JSON files")

        for json_file in json_files:
            logging.info(f"\n--- Loading {json_file.name} ---")
            bundle = _load_bundle_from_file(str(json_file))
            
            if bundle:
                loaded_bundles.append({
                    'filename': json_file.name,
                    'bundle': bundle,
                    'path': str(json_file)
                })
                logging.info(f"Successfully loaded bundle: {json_file.name}")
                logging.info(f"Bundle ID: {bundle.id if bundle.id else 'No ID'}")
                logging.info(f"Resource Type: {getattr(bundle, '__resource_type__', 'Bundle')}")
                if bundle.entry:
                    logging.info(f"Number of entries: {len(bundle.entry)}")
                    resource_types = [getattr(entry.resource, '__resource_type__', entry.resource.__class__.__name__) for entry in bundle.entry if entry.resource]
                    logging.info(f"Resource types: {set(resource_types)}")
            else:
                logging.error(f"Failed to load bundle: {json_file.name}")

    return loaded_bundles

def main():
    """
    Main function to test FHIR bundle loading.
    """
    logger.info("=== FHIR Bundle Loading Test ===")
    
    bundles = load_fhir_bundles_from_directory()

    logger.info(f"\n=== Summary ===")
    logger.info(f"Successfully loaded {len(bundles)} FHIR bundles")

    for bundle_info in bundles:
        logger.info(f"\nBundle: {bundle_info['filename']}")
        bundle = bundle_info['bundle']
        if bundle.entry:
            logger.info(f"  Entries: {len(bundle.entry)}")
            for i, entry in enumerate(bundle.entry):
                if entry.resource:
                    resource_type = getattr(entry.resource, '__resource_type__', entry.resource.__class__.__name__)
                    logger.info(f"    [{i}] {resource_type} - ID: {entry.resource.id if entry.resource.id else 'No ID'}")

if __name__ == "__main__":
    main()

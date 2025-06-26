import requests
import json
import os
from pathlib import Path
from typing import Optional
import logging

from app_config import BUNDLES_DIR

from fhir.resources.patient import Patient
from fhir.resources.bundle import Bundle

logger = logging.getLogger(__name__)

def get_patient_data(patient_id: str, base_url: str):
    """
    Fetches a Patient resource using requests and parses it with fhir.resources.
    """
    patient_url = f"{base_url}/Patient/{patient_id}"
    headers = {'Accept': 'application/fhir+json'}

    logger.info(f"Attempting to fetch: {patient_url}")

    try:
        response = requests.get(patient_url, headers=headers)
        response.raise_for_status()

        patient_data = response.json()
        patient = Patient.model_validate(patient_data)

        logger.info(f"Successfully fetched and parsed Patient ID: {patient.id}")

        return patient

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            logger.error(f"Error: Patient with ID '{patient_id}' not found on server.")
        else:
            logger.error(f"HTTP Error occurred: {err.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Network Error occurred: {e}")
        return None
    except (json.JSONDecodeError) as e:
        logger.error(f"Error parsing FHIR data: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None

def get_patient_data_dict(patient):
    patient_data = {
        "name": None,
        "date_of_birth": None,
        "gender": None,
    }

    if patient:
        patient_data["name"] = " ".join([name.given[0] + " " + name.family for name in patient.name]) if patient.name else None
        patient_data["date_of_birth"] = patient.birthDate if hasattr(patient, 'birthDate') else None
        patient_data["gender"] = patient.gender if hasattr(patient, 'gender') else None
    logger.info(f"Extracted patient data: {patient_data}")

    return patient_data

def _load_bundle_from_file(file_path: str) -> Optional[Bundle]:
    """
    Loads a FHIR Bundle resource from a JSON file.

    Args:
        file_path: The path to the JSON file containing the FHIR Bundle.

    Returns:
        The FHIR Bundle object, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        logger.error(f"Error: File not found at {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file {file_path}: {e}")
        return None
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading file {file_path}: {e}")
        return None

    try:
        bundle = Bundle.model_validate(data)
        if bundle:
            logger.info(f"Successfully loaded FHIR Bundle from {file_path}")
            return bundle
        else:
            logger.error(f"Error: Could not parse FHIR Bundle from file {file_path}. Validation returned None.")
            return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while parsing FHIR Bundle from {file_path}: {e}")
        return None

def load_fhir_bundles(patient_id) -> list:
    """
    Load all FHIR bundles for a given patient_id from the configured directory.
    Prints summary information about each bundle.
    Returns a list of loaded bundles with metadata.
    """
    bundles_dir = Path(BUNDLES_DIR) / patient_id

    logger.info(f"Looking for FHIR bundles in: {bundles_dir}")

    if not bundles_dir.exists():
        logger.error(f"Error: Directory {bundles_dir} does not exist")
        return []

    loaded_bundles = []
    json_files = list(bundles_dir.glob("*.json"))

    if not json_files:
        logger.error("No JSON files found in the bundles directory")
        return []

    logger.info(f"Found {len(json_files)} JSON files")

    for json_file in json_files:
        logger.info(f"\n--- Loading {json_file.name} ---")
        bundle = _load_bundle_from_file(str(json_file))

        if bundle:
            loaded_bundles.append({
                'filename': json_file.name,
                'bundle': bundle,
                'path': str(json_file)
            })
            logger.info(f"Successfully loaded bundle: {json_file.name}")
        else:
            logger.error(f"Failed to load bundle: {json_file.name}")

    return loaded_bundles
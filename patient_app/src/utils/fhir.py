import requests
import json
import os
from typing import Optional

from fhir.resources.patient import Patient
from fhir.resources.resource import Resource
from fhir.resources.bundle import Bundle

def get_patient_data(patient_id: str, base_url: str):
    """
    Fetches a Patient resource using requests and parses it with fhir.resources.
    """
    patient_url = f"{base_url}/Patient/{patient_id}"
    headers = {'Accept': 'application/fhir+json'}

    print(f"Attempting to fetch: {patient_url}")

    try:
        response = requests.get(patient_url, headers=headers)
        response.raise_for_status()

        patient_data = response.json()
        patient = Patient.model_validate(patient_data)

        print(f"Successfully fetched and parsed Patient ID: {patient.id}")

        return patient

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            print(f"Error: Patient with ID '{patient_id}' not found on server.")
        else:
            print(f"HTTP Error occurred: {err.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network Error occurred: {e}")
        return None
    except (json.JSONDecodeError) as e:
        print(f"Error parsing FHIR data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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
    print(patient_data)

    return patient_data

def load_bundle_from_file(file_path: str) -> Optional[Bundle]:
    """
    Loads a FHIR Bundle resource from a JSON file.

    Args:
        file_path: The path to the JSON file containing the FHIR Bundle.

    Returns:
        The FHIR Bundle object, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {file_path}: {e}")
        return None
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading file {file_path}: {e}")
        return None

    try:
        bundle = Bundle.model_validate(data)
        if bundle:
            print(f"Successfully loaded FHIR Bundle from {file_path}")
            return bundle
        else:
            print(f"Error: Could not parse FHIR Bundle from file {file_path}. Validation returned None.")
            return None
    except Exception as e:
        print(f"An unexpected error occurred while parsing FHIR Bundle from {file_path}: {e}")
        return None



if __name__ == "__main__":
    
    file_path = "/root/agedap-medical/patient_app/src/data/fhir_bundles/breast_cancer_bundle.json"
    fhir_bundle = load_bundle_from_file(file_path)
    if fhir_bundle:
        print(f"Loaded FHIR resource: {fhir_bundle.get_resource_type()}, Entries: {len(fhir_bundle.entry) if fhir_bundle.entry else 0}")

    file_path = "/root/agedap-medical/patient_app/src/data/fhir_bundles/diabetes_bundle.json"
    fhir_bundle = load_bundle_from_file(file_path)
    if fhir_bundle:
        print(f"Loaded FHIR resource: {fhir_bundle.get_resource_type()}, Entries: {len(fhir_bundle.entry) if fhir_bundle.entry else 0}")
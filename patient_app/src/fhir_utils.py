import fhir.resources.humanname
import requests
import json
from fhir.resources.patient import Patient

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

#temporal function for storing data 
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
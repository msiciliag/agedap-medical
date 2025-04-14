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
        print(patient_data)
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
    
if __name__ == "__main__":
    retrieved_patient = get_patient_data(80219, 'https://hapi.fhir.org/baseR5')

    if retrieved_patient:
        print(f"\nRetrieved Patient Object ID: {retrieved_patient.id}")

        # <<< --- ADD THE SAVING STEP HERE --- >>
        # <<< --- END SAVING STEP --- >>>

        # Now you can continue with your app's logic using the retrieved_patient object
        # ...
    else:
        print("\nFailed to retrieve patient data. Cannot save.")
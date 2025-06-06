import fhir.resources.humanname
import requests
import json
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
import os

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

def fetch_and_store_observation(obs_id: str, patient_id: str, base_url: str):
    """
    Descarga un recurso Observation de FHIR y lo almacena en la base OMOP-CDM.
    """
    url = f"{base_url}/Observation/{obs_id}"
    headers = {'Accept': 'application/fhir+json'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    obs_data = response.json()
    obs = Observation.model_validate(obs_data)

    # Almacenar en OMOP usando save_measurement_from_fhir
    from omop_utils import save_measurement_from_fhir
    save_measurement_from_fhir(obs, patient_id)
    print(f"Observation '{obs_id}' almacenada en OMOP para paciente {patient_id}")

def generate_example_measurement_files(output_dir: str = "src/fhir_data"):
    """
    Genera archivos JSON de ejemplo con Observations FHIR para cada modelo.
    """
    os.makedirs(output_dir, exist_ok=True)

    bc_features = [
        "radius1","texture1","perimeter1","area1","smoothness1","compactness1","concavity1","concave_points1","symmetry1","fractal_dimension1",
        "radius2","texture2","perimeter2","area2","smoothness2","compactness2","concavity2","concave_points2","symmetry2","fractal_dimension2",
        "radius3","texture3","perimeter3","area3","smoothness3","compactness3","concavity3","concave_points3","symmetry3","fractal_dimension3"
    ]
    bc_values = [
        13.54,14.36,87.46,566.3,0.09779,0.08129,0.06664,0.04781,0.1885,0.05766,
        0.2699,0.7886,2.058,23.56,0.008462,0.01460,0.02387,0.01315,0.01980,0.002300,
        15.11,19.26,99.70,711.2,0.14400,0.17730,0.23900,0.12880,0.2977,0.07259
    ]
    bc_resources = []
    for feature, value in zip(bc_features, bc_values):
        bc_resources.append({
            "resourceType": "Observation",
            "id": f"obs-{feature}",
            "status": "final",
            "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": "laboratory"}]}],
            "code": {"coding": [{"system": "http://example.org/fhir/bc-codes","code": feature,"display": feature}]},
            "subject": {"reference": "Patient/758718"},
            "effectiveDateTime": "2025-06-05T08:00:00Z",
            "valueQuantity": {"value": value,"unit": "units","system": "http://unitsofmeasure.org","code": "units"}
        })
    bc_path = os.path.join(output_dir, "breast_cancer_measurements.json")
    with open(bc_path, 'w', encoding='utf-8') as f:
        json.dump(bc_resources, f, indent=2)
    print(f"Archivo de Breast Cancer escrito en: {bc_path}")

    dm_features = [
        "HighBP","HighChol","CholCheck","BMI","Smoker","Stroke","HeartDiseaseorAttack",
        "PhysActivity","Fruits","Veggies","HvyAlcoholConsump","AnyHealthcare","NoDocbcCost",
        "GenHlth","MentHlth","PhysHlth","DiffWalk","Sex","Age","Education","Income"
    ]
    dm_values = [
        1,0,1,25,0,0,0,1,1,1,0,1,0,3,2,0,0,1,35,4,6
    ]
    dm_resources = []
    for feature, value in zip(dm_features, dm_values):
        dm_resources.append({
            "resourceType": "Observation",
            "id": f"obs-{feature}",
            "status": "final",
            "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": "survey"}]}],
            "code": {"coding": [{"system": "http://example.org/fhir/dm-codes","code": feature,"display": feature}]},
            "subject": {"reference": "Patient/758718"},
            "effectiveDateTime": "2025-06-05T08:00:00Z",
            "valueQuantity": {"value": value,"unit": "1","system": "http://unitsofmeasure.org","code": "1"}
        })
    dm_path = os.path.join(output_dir, "diabetes_measurements.json")
    with open(dm_path, 'w', encoding='utf-8') as f:
        json.dump(dm_resources, f, indent=2)
    print(f"Archivo de Diabetes escrito en: {dm_path}")

def push_and_sync_measurements(patient_id: str, base_url: str, schema: list):
    """
    Para cada feature en schema, comprueba si existe el Observation en FHIR sandbox.
    Si no existe, lo crea y lo sube. Luego descarga y almacena en OMOP.
    """
    # Función para construir un recurso Observation simple en memoria
    def build_observation(feature, value, category_code, code_system, unit_code="units"):
        return {
            "resourceType": "Observation",
            "id": f"obs-{feature}",
            "status": "final",
            "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": category_code}]}],
            "code": {"coding": [{"system": code_system,"code": feature,"display": feature}]},
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": "2025-06-05T08:00:00Z",
            "valueQuantity": {"value": value,"unit": unit_code,"system": "http://unitsofmeasure.org","code": unit_code}
        }

    # Determinar detalles según schema
    # Asumimos que breast cancer y diabetes usan distintos code_system y category_code
    if len(schema) == 30:
        category_code = "laboratory"
        code_system = "http://example.org/fhir/bc-codes"
        # ejemplo de valores, pueden extraerse de mock_data
        values = [float(v) for v in schema.values()] if isinstance(schema, dict) else None
        # Si schema es lista, usar fhir_utils.generate_example_measurement_files como fallback
        values = values or []
    else:
        category_code = "survey"
        code_system = "http://example.org/fhir/dm-codes"

    # Subida y sincronización
    for feature in schema:
        obs_id = f"obs-{feature}"
        url = f"{base_url}/Observation/{obs_id}"
        resp = requests.get(url)
        if resp.status_code == 404:
            from omop_utils import get_mock_value
            value = get_mock_value(feature)
            resource = build_observation(feature, value, category_code, code_system)
            headers = {'Content-Type': 'application/fhir+json'}
            put_resp = requests.put(url, headers=headers, json=resource)
            put_resp.raise_for_status()
        # Siempre descargar y almacenar en OMOP
        fetch_and_store_observation(obs_id, patient_id, base_url)
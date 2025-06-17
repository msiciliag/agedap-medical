#TODO: using a .py for config is not a good practice, but for simplicity
# it will be used for now. In a production app, consider using environment variables or a config management system.

STORAGE_PREFIX = "agedap.medical."
CONFIG_DONE_KEY = f"{STORAGE_PREFIX}config_done"
NAME_KEY = f"{STORAGE_PREFIX}name"
DOB_KEY = f"{STORAGE_PREFIX}date_of_birth"
GENDER_KEY = f"{STORAGE_PREFIX}gender"
SESSION_PATIENT_ID_KEY = f"{STORAGE_PREFIX}session_patient_id"
SESSION_HOSPITAL_URL_KEY = f"{STORAGE_PREFIX}hospital_url"
SESSION_HOSPITAL_NAME_KEY = f"{STORAGE_PREFIX}hospital_name"

# comprehensive list of keys managed by the app for client_storage
# used for clearing storage on logout or initial app start.
APP_LEVEL_STORAGE_KEYS = [
    CONFIG_DONE_KEY, NAME_KEY, DOB_KEY, GENDER_KEY,
    SESSION_PATIENT_ID_KEY, SESSION_HOSPITAL_URL_KEY, SESSION_HOSPITAL_NAME_KEY
]

USER_PATIENT_IDS = {
    "alice": "758718",
    "maria": "758734",
}

HOSPITAL_LIST = {
    "Hospital Universitario Ramón Y Cajal": 'https://hapi.fhir.org/baseR5',
    "Hospital Universitario 12 de Octubre": 'https://hapi.fhir.org/baseR5',
}

SERVICE_CONFIGS = {
    "breast_cancer": {"url": "http://localhost:5001", "fhe_directory": "/tmp/breast_cancer_fhe_files/", "key_directory": "/tmp/keys_client_fhe/"},
    "diabetes": {"url": "http://localhost:5002", "fhe_directory": "/tmp/diabetes_fhe_files/", "key_directory": "/tmp/keys_client_fhe/"},
}

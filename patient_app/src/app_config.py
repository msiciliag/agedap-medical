# app_config.py

STORAGE_PREFIX = "agedap.medical."
CONFIG_DONE_KEY = f"{STORAGE_PREFIX}config_done"
NAME_KEY = f"{STORAGE_PREFIX}name"
DOB_KEY = f"{STORAGE_PREFIX}date_of_birth"
GENDER_KEY = f"{STORAGE_PREFIX}gender"
SESSION_PATIENT_ID_KEY = f"{STORAGE_PREFIX}session_patient_id"
SESSION_HOSPITAL_URL_KEY = f"{STORAGE_PREFIX}hospital_url"
SESSION_HOSPITAL_NAME_KEY = f"{STORAGE_PREFIX}hospital_name"

# Comprehensive list of keys managed by the app for client_storage
# Useful for clearing storage on logout or initial app start.
APP_LEVEL_STORAGE_KEYS = [
    CONFIG_DONE_KEY, NAME_KEY, DOB_KEY, GENDER_KEY,
    SESSION_PATIENT_ID_KEY, SESSION_HOSPITAL_URL_KEY, SESSION_HOSPITAL_NAME_KEY
]

USER_PATIENT_IDS = {
    "alice": "758718",
    "john": "35552",
}

HOSPITAL_LIST = {
    "Hospital Universitario Ramón Y Cajal": 'https://hapi.fhir.org/baseR5',
    "Hospital Universitario 12 de Octubre": 'https://hapi.fhir.org/baseR5',
}
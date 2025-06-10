import json

class DynamicFHIRtoOMOPMapper:
    def __init__(self, fhir_reqs, omop_reqs):
        """
        Initializes the mapper with FHIR and OMOP requirements.
        fhir_reqs: A list of dictionaries describing FHIR requirements.
        omop_reqs: A dictionary (from JSON) describing OMOP requirements (e.g., {"measurement": [...]}).
        """
        self.fhir_reqs = fhir_reqs
        self.omop_reqs = omop_reqs
        self.transformation_map = self._build_transformation_map()

    def _build_transformation_map(self):
        """
        Builds an internal transformation map.
        Key: tuple (fhir_system, fhir_code)
        Value: Corresponding OMOP requirement dictionary from omop_reqs.measurement or omop_reqs.procedure etc.
               and the fhir_value_type.
        """
        internal_map = {}
        
        omop_measurements_map = {
            item["value_name"]: item for item in self.omop_reqs.get("measurement", [])
        }
        # Add other OMOP domains if necessary (e.g., procedure, observation)
        # omop_procedures_map = {
        #     item["procedure_source_value"]: item for item in self.omop_reqs.get("procedure", [])
        # }

        for fhir_item in self.fhir_reqs:
            fhir_code_info = fhir_item.get("fhir_code", {})
            fhir_system = fhir_code_info.get("system")
            fhir_code = fhir_code_info.get("code")
            link_name = fhir_item.get("name") # This 'name' links to OMOP's 'value_name'

            if fhir_system and fhir_code and link_name:
                # Prioritize measurement mapping based on current structure
                if link_name in omop_measurements_map:
                    omop_detail = omop_measurements_map[link_name]
                    internal_map[(fhir_system, fhir_code)] = {
                        "omop_domain": "measurement",
                        "omop_item_details": omop_detail,
                        "fhir_value_type": fhir_item.get("fhir_value_type"),
                        "fhir_resource_type": fhir_item.get("fhir_resource_type")
                    }
                # Example for procedure if it were structured with a 'name' for linking
                # elif link_name in omop_procedures_map:
                #     omop_detail = omop_procedures_map[link_name]
                #     internal_map[(fhir_system, fhir_code)] = {
                #         "omop_domain": "procedure",
                #         "omop_item_details": omop_detail,
                #         "fhir_value_type": fhir_item.get("fhir_value_type"), # May not be applicable
                #         "fhir_resource_type": fhir_item.get("fhir_resource_type")
                #     }
        return internal_map

    def transform_bundle(self, fhir_bundle):
        """
        Transforms a FHIR bundle into a list of OMOP records.
        fhir_bundle: A Python dictionary representing the FHIR bundle.
        """
        omop_records = []
        if not isinstance(fhir_bundle, dict) or "entry" not in fhir_bundle:
            print("Warning: Invalid FHIR bundle format.")
            return omop_records

        for entry in fhir_bundle.get("entry", []):
            resource = entry.get("resource")
            if not resource or not isinstance(resource, dict):
                continue

            resource_type = resource.get("resourceType")
            codings = resource.get("code", {}).get("coding", [])
            
            if not codings:
                continue

            # Attempt to map using the first coding entry
            # More sophisticated logic might iterate or prioritize codings
            fhir_system = codings[0].get("system")
            fhir_code_val = codings[0].get("code")

            mapping_rule = self.transformation_map.get((fhir_system, fhir_code_val))

            if mapping_rule and mapping_rule.get("fhir_resource_type") == resource_type:
                omop_item_details = mapping_rule["omop_item_details"]
                omop_domain = mapping_rule["omop_domain"]
                
                # Extract person_id and date from FHIR resource
                person_id_str = resource.get("subject", {}).get("reference", "Patient/Unknown").split("/")[-1]
                try:
                    person_id = int(person_id_str)
                except ValueError:
                    person_id = 0 # Or handle as appropriate

                # Defaulting type_concept_id, can be made more dynamic
                # 32817: EHR, 32865: Lab result, 32855: Derived value
                type_concept_id = 32817 


                if omop_domain == "measurement":
                    value_field_name = mapping_rule.get("fhir_value_type") # e.g., "valueQuantity"
                    value_data = resource.get(value_field_name) if value_field_name else None
                    
                    actual_value = None
                    if value_data and "value" in value_data:
                        actual_value = value_data["value"]
                    
                    # effectiveDateTime is preferred for measurements
                    event_datetime_str = resource.get("effectiveDateTime")
                    event_date_str = event_datetime_str[:10] if event_datetime_str else "1900-01-01"


                    omop_record = {
                        "domain_id": "Measurement",
                        "person_id": person_id,
                        "measurement_concept_id": omop_item_details.get("measurement_concept_id"),
                        "measurement_date": event_date_str,
                        "measurement_datetime": event_datetime_str or f"{event_date_str}T00:00:00Z",
                        "measurement_type_concept_id": type_concept_id, 
                        "value_as_number": float(actual_value) if actual_value is not None else None,
                        "value_source_value": str(actual_value) if actual_value is not None else None,
                        "measurement_source_value": omop_item_details.get("measurement_source_value"),
                        "measurement_source_concept_id": 0, # Default if not specified
                        "unit_source_value": value_data.get("unit") if value_data else None,
                        # Other fields like operator_concept_id, range_low, range_high, provider_id, visit_occurrence_id etc.
                        # would need more context or data in the FHIR resource or mapping rules.
                    }
                    if actual_value is not None: # Only add record if there's a value
                        omop_records.append(omop_record)

                # elif omop_domain == "procedure":
                #     # Handle procedure mapping
                #     # Procedures have procedure_date and procedure_datetime
                #     event_datetime_str = resource.get("performedDateTime") or resource.get("performedPeriod", {}).get("start")
                #     event_date_str = event_datetime_str[:10] if event_datetime_str else "1900-01-01"
                    
                #     omop_record = {
                #         "domain_id": "Procedure",
                #         "person_id": person_id,
                #         "procedure_concept_id": omop_item_details.get("procedure_concept_id"),
                #         "procedure_date": event_date_str,
                #         "procedure_datetime": event_datetime_str or f"{event_date_str}T00:00:00Z",
                #         "procedure_type_concept_id": type_concept_id, # e.g. 38000275 EHR order entry
                #         "procedure_source_value": omop_item_details.get("procedure_source_value"),
                #         "procedure_source_concept_id": 0,
                #     }
                #     omop_records.append(omop_record)
        
        return omop_records

'''EXAMPLE OF USE: 
import flet as ft
from app_config import APP_LEVEL_STORAGE_KEYS 
from navigation import route_change_handler, view_pop_handler
from app_init import initialize_application
import requests # Added for HTTP requests
import json     # Added for loading JSON bundle
from pathlib import Path # Added for path manipulation

# Assuming dynamic_mapper.py is in the same directory or accessible via Python path
from dynamic_mapper import DynamicFHIRtoOMOPMapper


def run_dynamic_etl_demonstration():
    print("Starting dynamic ETL demonstration...")
    service_base_url = "http://localhost:5001" # Assuming provider service runs here
    service_name = "Breast Cancer Screening" # Target service

    # 1. Fetch OMOP requirements
    try:
        omop_req_url = f"{service_base_url}/{service_name}/omop_requirements"
        print(f"Fetching OMOP requirements from: {omop_req_url}")
        response_omop = requests.get(omop_req_url)
        response_omop.raise_for_status() # Raise an exception for HTTP errors
        omop_requirements = response_omop.json()
        print("Successfully fetched OMOP requirements.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching OMOP requirements: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding OMOP requirements JSON: {e}")
        return

    # 2. Fetch FHIR requirements
    try:
        fhir_req_url = f"{service_base_url}/{service_name}/fhir_requirements"
        print(f"Fetching FHIR requirements from: {fhir_req_url}")
        response_fhir = requests.get(fhir_req_url)
        response_fhir.raise_for_status()
        fhir_requirements = response_fhir.json()
        print("Successfully fetched FHIR requirements.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching FHIR requirements: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding FHIR requirements JSON: {e}")
        return

    # 3. Instantiate DynamicFHIRtoOMOPMapper
    print("Instantiating DynamicFHIRtoOMOPMapper...")
    mapper = DynamicFHIRtoOMOPMapper(fhir_reqs=fhir_requirements, omop_reqs=omop_requirements)
    print("Mapper instantiated.")

    # 4. Load input FHIR bundle and use the mapper
    # Assuming breast_cancer_bundle.json is in patient_app/src/data/fhir_bundles/
    try:
        # Construct the path relative to this file's location or use an absolute path
        # For this example, let's assume it's in a known relative path
        current_dir = Path(__file__).parent
        bundle_path = current_dir / "data" / "fhir_bundles" / "breast_cancer_bundle.json"
        
        print(f"Loading FHIR bundle from: {bundle_path}")
        with open(bundle_path, 'r') as f:
            fhir_bundle_data = json.load(f)
        print("FHIR bundle loaded.")

        print("Transforming FHIR bundle to OMOP records...")
        omop_results = mapper.transform_bundle(fhir_bundle_data)
        print("Transformation complete.")
    except FileNotFoundError:
        print(f"Error: FHIR bundle file not found at {bundle_path}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding FHIR bundle JSON: {e}")
        return
    except Exception as e:
        print(f"An error occurred during transformation: {e}")
        return

    # 5. Print results
    print("\n--- Transformed OMOP Records ---")
    if omop_results:
        for record in omop_results:
            print(json.dumps(record, indent=2))
    else:
        print("No OMOP records were generated.")
    print("--- End of Transformed OMOP Records ---")
    print("\nDynamic ETL demonstration finished.")


def main(page: ft.Page):
    page.title = "AI HealthVault"
    page.adaptive = True

    for key in APP_LEVEL_STORAGE_KEYS:
        if page.client_storage.contains_key(key):
            page.client_storage.remove(key)

    page.window_width = 390
    page.window_height = 844
    page.window_resizable = False
    page.window_maximizable = False

    page.on_route_change = lambda route_event: route_change_handler(page, route_event.route)
    page.on_view_pop = lambda view_pop_event: view_pop_handler(page, view_pop_event)

    print("App starting...")
    
    # Run the demonstration logic. 
    # In a real app, this might be triggered by a user action or a specific app state.
    # For now, we call it directly after app initialization for demonstration.
    # Ensure the provider service (e.g., breast_cancer_screening_server.py) is running.
    # run_dynamic_etl_demonstration() # You can uncomment this to run on app start

    page.go("/login")

if __name__ == "__main__":
    # Initialize the application (database, etc.)
    initialize_application()
    
    # For demonstration purposes, you can run the ETL logic here before starting the Flet app
    # Ensure the provider service (e.g., breast_cancer_screening_server.py) is running on localhost:5001
    # run_dynamic_etl_demonstration() 
    # Comment out the above line if you don't want it to run automatically every time.
    # You might want to trigger this from a button in your Flet UI instead for testing.

    # Start the Flet app
    ft.app(target=main)
```

**To test this:**
1.  Ensure the `provider/services/breast_cancer_screening_server.py` is running (e.g., `python provider/services/breast_cancer_screening_server.py`). It should be accessible at `http://localhost:5001`.
2.  Make sure the `patient_app/src/data/fhir_bundles/breast_cancer_bundle.json` file exists and is correctly pathed in `main.py`.
3.  You can uncomment the `run_dynamic_etl_demonstration()` call in `patient_app/src/main.py` (either in `main` or in the `if __name__ == "__main__":` block) to see the output in the console when you run the patient app.
4.  Run the patient app (e.g., `python patient_app/src/main.py`).

This setup provides a foundation for a schema-driven ETL process. The `DynamicFHIRtoOMOPMapper` can be extended to handle more complex mappings, different FHIR resource types, and other OMOP domains as your services evolve.// filepath: /root/agedap-medical/patient_app/src/dynamic_mapper.py
import json

class DynamicFHIRtoOMOPMapper:
    def __init__(self, fhir_reqs, omop_reqs):
        """
        Initializes the mapper with FHIR and OMOP requirements.
        fhir_reqs: A list of dictionaries describing FHIR requirements.
        omop_reqs: A dictionary (from JSON) describing OMOP requirements (e.g., {"measurement": [...]}).
        """
        self.fhir_reqs = fhir_reqs
        self.omop_reqs = omop_reqs
        self.transformation_map = self._build_transformation_map()

    def _build_transformation_map(self):
        """
        Builds an internal transformation map.
        Key: tuple (fhir_system, fhir_code)
        Value: Corresponding OMOP requirement dictionary from omop_reqs.measurement or omop_reqs.procedure etc.
               and the fhir_value_type.
        """
        internal_map = {}
        
        omop_measurements_map = {
            item["value_name"]: item for item in self.omop_reqs.get("measurement", [])
        }
        # Add other OMOP domains if necessary (e.g., procedure, observation)
        # omop_procedures_map = {
        #     item["procedure_source_value"]: item for item in self.omop_reqs.get("procedure", [])
        # }

        for fhir_item in self.fhir_reqs:
            fhir_code_info = fhir_item.get("fhir_code", {})
            fhir_system = fhir_code_info.get("system")
            fhir_code = fhir_code_info.get("code")
            link_name = fhir_item.get("name") # This 'name' links to OMOP's 'value_name'

            if fhir_system and fhir_code and link_name:
                # Prioritize measurement mapping based on current structure
                if link_name in omop_measurements_map:
                    omop_detail = omop_measurements_map[link_name]
                    internal_map[(fhir_system, fhir_code)] = {
                        "omop_domain": "measurement",
                        "omop_item_details": omop_detail,
                        "fhir_value_type": fhir_item.get("fhir_value_type"),
                        "fhir_resource_type": fhir_item.get("fhir_resource_type")
                    }
                # Example for procedure if it were structured with a 'name' for linking
                # elif link_name in omop_procedures_map:
                #     omop_detail = omop_procedures_map[link_name]
                #     internal_map[(fhir_system, fhir_code)] = {
                #         "omop_domain": "procedure",
                #         "omop_item_details": omop_detail,
                #         "fhir_value_type": fhir_item.get("fhir_value_type"), # May not be applicable
                #         "fhir_resource_type": fhir_item.get("fhir_resource_type")
                #     }
        return internal_map

    def transform_bundle(self, fhir_bundle):
        """
        Transforms a FHIR bundle into a list of OMOP records.
        fhir_bundle: A Python dictionary representing the FHIR bundle.
        """
        omop_records = []
        if not isinstance(fhir_bundle, dict) or "entry" not in fhir_bundle:
            print("Warning: Invalid FHIR bundle format.")
            return omop_records

        for entry in fhir_bundle.get("entry", []):
            resource = entry.get("resource")
            if not resource or not isinstance(resource, dict):
                continue

            resource_type = resource.get("resourceType")
            codings = resource.get("code", {}).get("coding", [])
            
            if not codings:
                continue

            # Attempt to map using the first coding entry
            # More sophisticated logic might iterate or prioritize codings
            fhir_system = codings[0].get("system")
            fhir_code_val = codings[0].get("code")

            mapping_rule = self.transformation_map.get((fhir_system, fhir_code_val))

            if mapping_rule and mapping_rule.get("fhir_resource_type") == resource_type:
                omop_item_details = mapping_rule["omop_item_details"]
                omop_domain = mapping_rule["omop_domain"]
                
                # Extract person_id and date from FHIR resource
                person_id_str = resource.get("subject", {}).get("reference", "Patient/Unknown").split("/")[-1]
                try:
                    person_id = int(person_id_str)
                except ValueError:
                    person_id = 0 # Or handle as appropriate

                # Defaulting type_concept_id, can be made more dynamic
                # 32817: EHR, 32865: Lab result, 32855: Derived value
                type_concept_id = 32817 


                if omop_domain == "measurement":
                    value_field_name = mapping_rule.get("fhir_value_type") # e.g., "valueQuantity"
                    value_data = resource.get(value_field_name) if value_field_name else None
                    
                    actual_value = None
                    if value_data and "value" in value_data:
                        actual_value = value_data["value"]
                    
                    # effectiveDateTime is preferred for measurements
                    event_datetime_str = resource.get("effectiveDateTime")
                    event_date_str = event_datetime_str[:10] if event_datetime_str else "1900-01-01"


                    omop_record = {
                        "domain_id": "Measurement",
                        "person_id": person_id,
                        "measurement_concept_id": omop_item_details.get("measurement_concept_id"),
                        "measurement_date": event_date_str,
                        "measurement_datetime": event_datetime_str or f"{event_date_str}T00:00:00Z",
                        "measurement_type_concept_id": type_concept_id, 
                        "value_as_number": float(actual_value) if actual_value is not None else None,
                        "value_source_value": str(actual_value) if actual_value is not None else None,
                        "measurement_source_value": omop_item_details.get("measurement_source_value"),
                        "measurement_source_concept_id": 0, # Default if not specified
                        "unit_source_value": value_data.get("unit") if value_data else None,
                        # Other fields like operator_concept_id, range_low, range_high, provider_id, visit_occurrence_id etc.
                        # would need more context or data in the FHIR resource or mapping rules.
                    }
                    if actual_value is not None: # Only add record if there's a value
                        omop_records.append(omop_record)

                # elif omop_domain == "procedure":
                #     # Handle procedure mapping
                #     # Procedures have procedure_date and procedure_datetime
                #     event_datetime_str = resource.get("performedDateTime") or resource.get("performedPeriod", {}).get("start")
                #     event_date_str = event_datetime_str[:10] if event_datetime_str else "1900-01-01"
                    
                #     omop_record = {
                #         "domain_id": "Procedure",
                #         "person_id": person_id,
                #         "procedure_concept_id": omop_item_details.get("procedure_concept_id"),
                #         "procedure_date": event_date_str,
                #         "procedure_datetime": event_datetime_str or f"{event_date_str}T00:00:00Z",
                #         "procedure_type_concept_id": type_concept_id, # e.g. 38000275 EHR order entry
                #         "procedure_source_value": omop_item_details.get("procedure_source_value"),
                #         "procedure_source_concept_id": 0,
                #     }
                #     omop_records.append(omop_record)
        
        return omop_records

```

### Tarea 3: Orquestar el Flujo Dinámico

Finally, update `patient_app/src/main.py` to demonstrate the dynamic flow. This example will use the `requests` library to fetch requirements from the running service and `json` to load the bundle. Ensure `requests` is installed in your environment (`pip install requests`).

````python
// filepath: /root/agedap-medical/patient_app/src/main.py
import flet as ft
from app_config import APP_LEVEL_STORAGE_KEYS 
from navigation import route_change_handler, view_pop_handler
from app_init import initialize_application
import requests # Added for HTTP requests
import json     # Added for loading JSON bundle
from pathlib import Path # Added for path manipulation

# Assuming dynamic_mapper.py is in the same directory or accessible via Python path
from dynamic_mapper import DynamicFHIRtoOMOPMapper


def run_dynamic_etl_demonstration():
    print("Starting dynamic ETL demonstration...")
    service_base_url = "http://localhost:5001" # Assuming provider service runs here
    service_name = "Breast Cancer Screening" # Target service

    # 1. Fetch OMOP requirements
    try:
        omop_req_url = f"{service_base_url}/{service_name}/omop_requirements"
        print(f"Fetching OMOP requirements from: {omop_req_url}")
        response_omop = requests.get(omop_req_url)
        response_omop.raise_for_status() # Raise an exception for HTTP errors
        omop_requirements = response_omop.json()
        print("Successfully fetched OMOP requirements.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching OMOP requirements: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding OMOP requirements JSON: {e}")
        return

    # 2. Fetch FHIR requirements
    try:
        fhir_req_url = f"{service_base_url}/{service_name}/fhir_requirements"
        print(f"Fetching FHIR requirements from: {fhir_req_url}")
        response_fhir = requests.get(fhir_req_url)
        response_fhir.raise_for_status()
        fhir_requirements = response_fhir.json()
        print("Successfully fetched FHIR requirements.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching FHIR requirements: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding FHIR requirements JSON: {e}")
        return

    # 3. Instantiate DynamicFHIRtoOMOPMapper
    print("Instantiating DynamicFHIRtoOMOPMapper...")
    mapper = DynamicFHIRtoOMOPMapper(fhir_reqs=fhir_requirements, omop_reqs=omop_requirements)
    print("Mapper instantiated.")

    # 4. Load input FHIR bundle and use the mapper
    # Assuming breast_cancer_bundle.json is in patient_app/src/data/fhir_bundles/
    try:
        # Construct the path relative to this file's location or use an absolute path
        # For this example, let's assume it's in a known relative path
        current_dir = Path(__file__).parent
        bundle_path = current_dir / "data" / "fhir_bundles" / "breast_cancer_bundle.json"
        
        print(f"Loading FHIR bundle from: {bundle_path}")
        with open(bundle_path, 'r') as f:
            fhir_bundle_data = json.load(f)
        print("FHIR bundle loaded.")

        print("Transforming FHIR bundle to OMOP records...")
        omop_results = mapper.transform_bundle(fhir_bundle_data)
        print("Transformation complete.")
    except FileNotFoundError:
        print(f"Error: FHIR bundle file not found at {bundle_path}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding FHIR bundle JSON: {e}")
        return
    except Exception as e:
        print(f"An error occurred during transformation: {e}")
        return

    # 5. Print results
    print("\n--- Transformed OMOP Records ---")
    if omop_results:
        for record in omop_results:
            print(json.dumps(record, indent=2))
    else:
        print("No OMOP records were generated.")
    print("--- End of Transformed OMOP Records ---")
    print("\nDynamic ETL demonstration finished.")


def main(page: ft.Page):
    page.title = "AI HealthVault"
    page.adaptive = True

    for key in APP_LEVEL_STORAGE_KEYS:
        if page.client_storage.contains_key(key):
            page.client_storage.remove(key)

    page.window_width = 390
    page.window_height = 844
    page.window_resizable = False
    page.window_maximizable = False

    page.on_route_change = lambda route_event: route_change_handler(page, route_event.route)
    page.on_view_pop = lambda view_pop_event: view_pop_handler(page, view_pop_event)

    print("App starting...")
    
    # Run the demonstration logic. 
    # In a real app, this might be triggered by a user action or a specific app state.
    # For now, we call it directly after app initialization for demonstration.
    # Ensure the provider service (e.g., breast_cancer_screening_server.py) is running.
    # run_dynamic_etl_demonstration() # You can uncomment this to run on app start

    page.go("/login")

if __name__ == "__main__":
    # Initialize the application (database, etc.)
    initialize_application()
    
    # For demonstration purposes, you can run the ETL logic here before starting the Flet app
    # Ensure the provider service (e.g., breast_cancer_screening_server.py) is running on localhost:5001
    # run_dynamic_etl_demonstration() 
    # Comment out the above line if you don't want it to run automatically every time.
    # You might want to trigger this from a button in your Flet UI instead for testing.

    # Start the Flet app
    ft.app(target=main)
```

**To test this:**
1.  Ensure the `provider/services/breast_cancer_screening_server.py` is running (e.g., `python provider/services/breast_cancer_screening_server.py`). It should be accessible at `http://localhost:5001`.
2.  Make sure the `patient_app/src/data/fhir_bundles/breast_cancer_bundle.json` file exists and is correctly pathed in `main.py`.
3.  You can uncomment the `run_dynamic_etl_demonstration()` call in `patient_app/src/main.py` (either in `main` or in the `if __name__ == "__main__":` block) to see the output in the console when you run the patient app.
4.  Run the patient app (e.g., `python patient_app/src/main.py`).

This setup provides a foundation for a schema-driven ETL process. The `DynamicFHIRtoOMOPMapper` can be extended to handle more complex mappings, different FHIR resource types, and other OMOP domains as your services evolve.
'''
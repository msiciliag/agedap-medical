# Patient Application

This directory contains the Flet-based patient-facing application. It is designed to interact with backend medical services, particularly those leveraging Fully Homomorphic Encryption (FHE) for privacy-preserving operations, as provided by the `provider/` component of the Agedap Medical project.

## Quickstart

To run the patient application:

```bash
uv run flet run patient_app/src/main.py
```
or
```bash
uv run flet run --web patient_app/src/main.py
```

This will launch the application, allowing you to interact with the configured medical services. Ensure that the provider services are running and accessible as configured in `patient_app/src/app_config.py`. Follow `/provider/README.md` for more details.

## Directory Structure

```
patient_app/
├── .gitignore
├── pyproject.toml
├── README.md                           
└── src/
    ├── api_client/
    │   ├── __init__.py
    │   └── base_client.py              # Base client for interacting with provider services
    ├── assets/
    │   ├── icon.png
    │   └── splash_android.png
    ├── views/
    │   ├── __init__.py
    │   ├── config_view.py              # View for configuring service endpoints
    │   ├── login_view.py               # View for user login (conceptual)
    │   ├── main_app_view.py            # Main view after login, listing services
    │   └── service_view.py             # View for interacting with a specific medical service
    ├── app_config.py                   # Application configuration (e.g., service URLs)
    ├── fhir_utils.py                   # Utilities for handling FHIR data (sandbox)
    ├── main.py                         # Main entry point for the Flet application
    ├── navigation.py                   # Handles navigation between different views
    └── omop_utils.py                   # Utilities for handling OMOP data (conceptual)
```

## Key Components

-   **`src/main.py`**: The main script that initializes and runs the Flet application. This is the entry point.
-   **`src/app_config.py`**: Manages application-level configurations, such as the URLs for the backend provider services. You may need to modify this file to point to the correct service endpoints or add new ones.
-   **`src/navigation.py`**: Controls the flow and transitions between different views (screens) within the application.
-   **`src/api_client/`**: Contains the logic for making requests to the backend AI services.
    -   `base_client.py`: Provides a foundational class for API communication, handling requests and responses.
-   **`src/views/`**: Each file in this directory represents a distinct view or screen in the application:
    -   `login_view.py`: A conceptual login screen.
    -   `config_view.py`: Allows users to view and potentially modify the configuration of backend service endpoints.
    -   `main_app_view.py`: The main screen after login, typically displaying a list of available medical services.
    -   `service_view.py`: Provides the interface for users to input data and receive results from a selected medical service.
-   **`src/fhir_utils.py` & `src/omop_utils.py`**: Placeholder utilities intended for future integration with FHIR and OMOP data standards, facilitating the handling of medical data in standardized formats.

## Features (Proof of Concept)

As a proof of concept, the patient application demonstrates:
-   A basic Flet UI structure.
-   Navigation between different views.
-   Configuration of service endpoints.
-   Interaction with backend FHE services (e.g., submitting data for prediction and displaying results).
-   Conceptual handling of medical data standards (FHIR/OMOP).

## Configuration

Service endpoints are primarily configured in `src/app_config.py`. Before running the application, ensure that the `SERVICE_CONFIGS` dictionary in this file correctly points to the running instances of the provider services (e.g., breast cancer screening, diabetes prediction).

The application also provides a "Configuration" view accessible from the navigation menu, which allows viewing the currently configured service URLs.

## Interacting with Services

1.  Launch the application using `uv run patient_app/src/main.py`.
2.  (Conceptually) Log in via the login screen.
3.  From the main application view, select an available medical service.
4.  The `service_view` will load, displaying information about the service and input fields based on its OMOP requirements.
5.  Submit your data automatically to the service selecing "Run Service".
6.  The application will communicate with the backend FHE service, and the encrypted results will be displayed.

This `README.md` provides an overview of the patient application component. For details on the backend services, refer to the `README.md` in the `provider/` directory.

## Adding New Services

After you have set up and started a new AI service on the provider side (as detailed in `provider/README.md`), you need to make the patient application aware of it. This is done by adding its configuration to the `SERVICE_CONFIGS` dictionary within the `patient_app/src/app_config.py` file.

The `SERVICE_CONFIGS` dictionary has the following structure:

```python
SERVICE_CONFIGS = {
    "service_key_name_1": {
        "url": "http://localhost:port1/",
        "fhe_directory": "/path/to/your/service1/fhe_model_files/",
        "key_directory": "/path/to/your/client_side_fhe_keys/"
    },
    "service_key_name_2": {
        "url": "http://localhost:port2/",
        "fhe_directory": "/path/to/your/service2/fhe_model_files/",
        "key_directory": "/path/to/your/client_side_fhe_keys/"
    },
    # ... add your new service here
}
```

To add your new service:

1.  **Choose a `service_key_name`**: This is a unique string identifier for your service within the patient application (e.g., `"heart_disease_prediction"`). This key will be used internally and to display the service name in the UI (often transformed, e.g., "Heart Disease Prediction").
2.  **Add a new entry** to the `SERVICE_CONFIGS` dictionary using this key.
3.  **Provide the configuration details** for your new service within the nested dictionary:
    *   `"url"`: The full URL where your new provider service is running (e.g., `"http://localhost:5003/"`). This must match the host and port configured for the service in `provider/training_config.yaml` and started by `provider/start_all.py` or manually.
    *   `"fhe_directory"`: The absolute path to the directory on the client machine where the FHE *model* files (generated by the provider during training, e.g., `server.zip`, `client.zip`) for this specific service are expected to be found. This path is used by the client to load necessary FHE components. Must be the same as the one defined in `provider/training_config.yaml`.
    *   `"key_directory"`: The absolute path to the directory on the client machine where the FHE client-side keys are stored.

**Example for a new "Kidney Disease Screening" service running on port 5003:**

```python
SERVICE_CONFIGS = {
    "breast_cancer": {
        "url": "http://localhost:5001/", 
        "fhe_directory": "/tmp/breast_cancer_fhe_files/", 
        "key_directory": "/tmp/keys_client_fhe/"
    },
    "diabetes": {
        "url": "http://localhost:5002/", 
        "fhe_directory": "/tmp/diabetes_fhe_files/", 
        "key_directory": "/tmp/keys_client_fhe/"
    },
    "kidney_disease": {  # New service entry
        "url": "http://localhost:5003/",
        "fhe_directory": "/tmp/kidney_disease_fhe_files/",
        "key_directory": "/tmp/keys_client_fhe/"  # Often, the key directory can be shared if keys are compatible or managed centrally
    }
}
```

After updating [`patient_app/src/app_config.py`](patient_app/src/app_config.py:0) with the new service configuration, restart the patient application. The new service should then appear in the list of available services in the UI if the servers are available.

# AI Model and Service Provider

This directory contains the components responsible for training, managing, and serving the AI models used within the Agedap Medical application. These models are designed to be compatible with ConcreteML library, which uses Fully Homomorphic Encryption (FHE) for secure predictions.

## Directory Structure

```
provider/
├── services/
│   ├── base_service.py                   # Base class for AI service endpoints
│   ├── breast_cancer_screening_server.py # Example: Flask breast cancer screening
│   ├── diabetes_prediction_server.py     # Example: Flask diabetes prediction
│   └── ...                               # Other service-specific server files
├── README.md                             
├── start_all.py                          # Script for orchestrating and starting all services
├── training_config.yaml                  # Configuration for model training and deployment
└── train.py                              # Script for training FHE models                           
```

-   **`services/`**: Contains the individual Flask-based server applications for each AI model.
    -   `base_service.py`: Provides a common structure and utilities for all AI service endpoints, including loading FHE models and defining common API routes like `/get_additional_service_info` and `/get_omop_requirements`.
    -   Each `*_server.py` file (e.g., `breast_cancer_screening_server.py`) implements a specific AI service, inheriting from `AIServiceEndpoint` in `base_service.py`. It loads its corresponding FHE model and exposes prediction endpoints.
-   **`start_all.py`**: A management script located at the project root that:
    - Checks whether the required FHE model artifacts exist.
    - Invokes `provider/train.py` to train and save any missing models.
    - Starts all configured Flask-based AI service endpoints, each running on its specified port.
-   **`training_config.yaml`**: A YAML configuration file that defines parameters for training various models. For each model, it specifies:
    -   `dataset_id`: The ID of the dataset from the UCI Machine Learning Repository.
    -   `output_directory`: The path where the trained FHE model files should be saved.
    -   `n_estimators`, `max_depth`: Hyperparameters for the model, only supported ones.
    -   `service_name`: A display name for the service.
    -   `server_script`: The path to the Flask server script for this model.
    -   `server_port`: The port on which the Flask server should run.
-   **`train.py`**: A script used to train machine learning models (e.g., RandomForestClassifier from `concrete-ml`) using datasets specified in `training_config.yaml`. It preprocesses data, trains the model, compiles it for FHE, and saves the FHE model artifacts to a specified directory.

## Model Training

Models are trained using the `train.py` script, which reads its configuration from `training_config.yaml`.

1.  **Configure `training_config.yaml`**: Define the datasets, model parameters, output directories, and server details for each model you want to train.
2.  **Run `train.py`**:
    ```bash
    python provider/train.py
    ```
    This will fetch the data, train the model(s), and save the FHE model artifacts (including `server.zip`, `client.zip`, etc.) to the respective `output_directory` specified in the configuration.
> [!TIP]
> For saving a model again, firstly you have to clear the artifacts already generated e.g.
>```bash
>sudo rm -r /tmp/breast_cancer_fhe_files/ /tmp/diabetes_fhe_files/
>```

## Running the AI Services

The AI services are Flask applications that load the pre-trained FHE models and expose endpoints for predictions and metadata.

Each service can be run individually:
```bash
python provider/services/breast_cancer_screening_server.py
python provider/services/diabetes_prediction_server.py
# etc.
```

Alternatively, a script like `start_all.py` (located in the project root `/root/agedap-medical/`) can be used to:
1.  Check if models defined in `provider/training_config.yaml` exist in their `output_directory`.
2.  Train any missing models using `provider/train.py`.
3.  Start all configured Flask servers in the background.

Refer to the `start_all.py` script and the main project README for more details on orchestrating these services.

## FHE Model Artifacts

The `train.py` script, using `concrete-ml`, generates FHE model artifacts in the specified `output_directory`. These typically include:
-   `server.zip`: Contains the FHE evaluation keys and the compiled model for the server-side.
-   `client.zip`: Contains the FHE encryption/decryption keys and client-side specifications.
-   Other metadata files.

The Flask servers in the `services/` directory load the `server.zip` to perform FHE predictions.

## Adding a New AI Service

1.  **Prepare Data and Model Logic**: Identify the dataset and the type of model.
2.  **Update `training_config.yaml`**: Add a new entry for your service, specifying its `dataset_id`, `output_directory`, model hyperparameters, `server_script` path, and `server_port`.
3.  **Create Server Script**: In the `provider/services/` directory, create a new Python script for your service (e.g., `new_service_server.py`).
    -   This script should define a class that inherits from `AIServiceEndpoint` (from `base_service.py`).
    -   Implement any service-specific logic.
    -   Ensure it initializes with the correct `service_name`, `model_display_name`, and `fhe_directory`.
4.  **Train the Model**: Run `python provider/train.py` or let `start_all.py` handle it. This will generate the FHE model in the specified `output_directory`.
5.  **Test**: Run your new service script directly or via `start_all.py` and test its endpoints.
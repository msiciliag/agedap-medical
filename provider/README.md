# AI Model and Service Provider

This directory contains the components responsible for training, managing, and serving the AI models used within the Agedap Medical application. These models are designed to be compatible with ConcreteML library, which uses Fully Homomorphic Encryption (FHE) for secure predictions.

## Quickstart
For training and starting the service servers use:

```bash
uv run provider/start_all.py
```

This scripts takes the configuration specified in **`training_config.yaml`**. The default content of this file defines two models: one for breast cancer screening and another for diabetes probability prediction.

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
-   **`start_all.py`**: A management script that takes `training_config.yaml` as an input and:
    - Checks whether the required FHE model artifacts specified in the configuration file exists.
    - Invokes `provider/train.py` to train and save any missing models following the parameters and dataset specifications in the yaml file.
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

Models are trained using the `train.py` script, which reads its configuration from `training_config.yaml`. If needed, you can train the models by your own:

1.  **Configure `training_config.yaml`**: Define the datasets, model parameters, output directories, and details for each model you want to train.
2.  **Run `train.py`**:
    ```bash
    uv run train.py
    ```
    This will fetch the data, train the model(s), and save the ConcreteML FHE model artifacts to the respective `output_directory` specified in the configuration.

> [!TIP]
> For saving a model again, you have to clear the artifacts already generated beforehand e.g.
>```bash
>sudo rm -r /tmp/breast_cancer_fhe_files/ 
>sudo rm -r /tmp/diabetes_fhe_files/
>```

## Running the AI Services

The AI services are Flask applications that load the pre-trained FHE models and expose endpoints for predictions and metadata.

Each service can be run individually:
```bash
uv run provider/services/breast_cancer_screening_server.py
uv run provider/services/diabetes_prediction_server.py
```

Or you can start all services running `start_all.py` to run them in the background.
```bash
uv run start_all.py
```

## Adding a New AI Service

1.  **Prepare Data and Model Logic**: Identify the dataset and the type of model.
2.  **Update `training_config.yaml`**: Add a new entry for your service, specifying its `dataset_id`, `output_directory`, model hyperparameters, `server_script` path, and `server_port`.
3.  **Create Server Script**: In the `provider/services/` directory, create a new Python script for your service (e.g., `new_service_server.py`).
    -   This script should define a class that inherits from `AIServiceEndpoint` (from `base_service.py`).
    -   Define `get_omop_requirements()` with the corresponding OMOP CMD scheme needed and `get_additional_service_info()` with the information you want to show to the consumer.
    -   Ensure it initializes with the correct `service_name`, `model_display_name`, and `fhe_directory`.
4.  **Train the Model**: Run `python provider/train.py`. Skip this step if using `start_all.py`.
5.  **Test**: Run your new service script directly or via `start_all.py` and test its endpoints.

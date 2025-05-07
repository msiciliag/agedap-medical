'''
This script trains a Random Forest Classifier model using datasets from the UCI Machine Learning Repository
and saves it as a FHE Model. It reads dataset parameters from a YAML configuration file.
'''

import yaml
from concrete.ml.sklearn import RandomForestClassifier
from concrete.ml.deployment import FHEModelDev
from ucimlrepo import fetch_ucirepo
from sklearn.preprocessing import LabelEncoder
import os

def load_data(dataset_id):
    """Fetch and preprocess the dataset."""
    uci_ds = fetch_ucirepo(id=dataset_id)
    X = uci_ds.data.features
    X = X.astype(float)
    y = uci_ds.data.targets
    le = LabelEncoder()
    y = le.fit_transform(y.values.ravel())
    y = y.astype(int)
    return X, y

def train_model(X, y, n_estimators=10, max_depth=5):
    """Train and compile the Random Forest model."""
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
    model.fit(X, y)
    model.compile(X)
    return model

def save_fhe_model(model, directory):
    """Save the trained model as an FHE model."""
    dev = FHEModelDev(path_dir=directory, model=model)
    dev.save()

def train_and_save(dataset_id, output_directory, n_estimators=10, max_depth=5):
    """Generic function to train and save a model for a given dataset."""
    X, y = load_data(dataset_id)
    model = train_model(X, y, n_estimators, max_depth)
    save_fhe_model(model, output_directory)

def load_config(config_path):
    """Load dataset configuration from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
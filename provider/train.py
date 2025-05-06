'''
This script trains a Random Forest Classifier model using datasets from the UCI Machine Learning Repository
and saves it as a FHE Model. It supports multiple datasets by parameterizing the dataset ID and output directory.
'''

from concrete.ml.sklearn import RandomForestClassifier
from concrete.ml.deployment import FHEModelDev
from ucimlrepo import fetch_ucirepo
from sklearn.preprocessing import LabelEncoder

def load_data(dataset_id):
    """Fetch and preprocess the dataset."""
    uci_ds = fetch_ucirepo(id=dataset_id)
    X = uci_ds.data.features
    y = uci_ds.data.targets
    le = LabelEncoder()
    y = le.fit_transform(y.values.ravel())
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

if __name__ == "__main__":

    train_and_save(
        dataset_id=17,  # Breast Cancer Wisconsin (Diagnostic) ds
        output_directory='/tmp/breast_cancer_fhe_files/',
        n_estimators=10,
        max_depth=5
    )

    train_and_save(
        dataset_id=891,  # CDC Diabetes Health Indicators ds
        output_directory='/tmp/diabetes_fhe_files/',
        n_estimators=10,
        max_depth=5
    )
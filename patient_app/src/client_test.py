from api_clients.breast_cancer_screening_client import BreastCancerClient
from omop_utils import get_data

if __name__ == "__main__":
    # Example usage:
    client = BreastCancerClient()

    info = client.request_info()
    required_features = info["omop_requirements"]["required_measurements_by_source_value"]
    X_new = get_data(required_features)

    for feat, val in zip(required_features, X_new[0]):
        print(f"{feat}: {val:.3f}")

    if X_new.size > 0:
        prediction = client.request_prediction(X_new)
        print("Decrypted prediction:", prediction)
    else:
        print("No input data available for prediction.")
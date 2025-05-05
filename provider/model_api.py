'''
This file is the API side of the FHE model. It is responsible for receiving
encrypted data from the client, running the model, and returning the encrypted result to the client.
It also provides metadata about the expected input structure.
'''

from concrete.ml.deployment import FHEModelServer
from flask import Flask, request, jsonify

fhe_directory = '/tmp/fhe_client_server_files/'

EXPECTED_FEATURES = [
    'mean radius', 'mean texture', 'mean perimeter', 'mean area', 'mean smoothness',
    'mean compactness', 'mean concavity', 'mean concave points', 'mean symmetry', 'mean fractal dimension',
    'radius error', 'texture error', 'perimeter error', 'area error', 'smoothness error',
    'compactness error', 'concavity error', 'concave points error', 'symmetry error', 'fractal dimension error',
    'worst radius', 'worst texture', 'worst perimeter', 'worst area', 'worst smoothness',
    'worst compactness', 'worst concavity', 'worst concave points', 'worst symmetry', 'worst fractal dimension'
]

server = FHEModelServer(path_dir=fhe_directory)
server.load()

app = Flask(__name__)

@app.route('/info', methods=['GET'])
def get_info():
    """Provides metadata about the expected input features."""
    metadata = {
        "omop_requirements": {
            "required_measurements_by_source_value": [
                "radius1",
                "texture1",
                "perimeter1",
                "area1",
                "smoothness1",
                "compactness1",
                "concavity1",
                "concave_points1",
                "symmetry1",
                "fractal_dimension1",
                "radius2",
                "texture2",
                "perimeter2",
                "area2",
                "smoothness2",
                "compactness2",
                "concavity2",
                "concave_points2",
                "symmetry2",
                "fractal_dimension2",
                "radius3",
                "texture3",
                "perimeter3",
                "area3",
                "smoothness3",
                "compactness3",
                "concavity3",
                "concave_points3",
                "symmetry3",
                "fractal_dimension3"
            ],
            "query_hint": "Retrieve measurements where measurement_concept_id = 0 and measurement_source_value is in the list above.",
            "expected_input_format": {
                "structure": "object_with_key_value_pairs",
                "key": "measurement_source_value",
                "value": "value_as_number"
            }
        },
        "fhe_evaluation_keys":{
            "key1": "value1",
            "key2": "value2"
        },
        "prediction_endpoint": "/predict",
        "prediction_method": "POST"
    }
    return jsonify(metadata)

@app.route('/predict', methods=['POST'])
def predict():
    """Receives encrypted data and evaluation keys, returns encrypted prediction."""
    try:
        encrypted_data_file = request.files.get('encrypted_data')
        evaluation_keys_file = request.files.get('evaluation_keys')

        if not encrypted_data_file or not evaluation_keys_file:
            return "Missing files in the request", 400

        encrypted_data = encrypted_data_file.read()
        serialized_evaluation_keys = evaluation_keys_file.read()

        encrypted_result = server.run(encrypted_data, serialized_evaluation_keys)

        return encrypted_result, 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        app.logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)

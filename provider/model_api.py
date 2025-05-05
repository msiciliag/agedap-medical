'''
This file is the API side of the FHE model. It is responsible for receiving
encrypted data from the client, running the model, and returning the encrypted result to the client.
It also provides metadata about the expected input structure.
'''

from concrete.ml.deployment import FHEModelServer
from flask import Flask, request, jsonify 
import base64

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
                #TODO add the rest of the params
                "fractal_dimension3"
            ],
            "query_hint": "Retrieve measurements where measurement_concept_id = 0 and measurement_source_value is in the list above.",
            "expected_input_format": { #TODO darle una vuelta a esto
                "structure": "object_with_key_value_pairs",
                "key": "measurement_source_value",
                "value": "value_as_number"
            }
        },
        #TODO add the fhe evaluation keys
        "prediction_endpoint": "/predict",
        "prediction_method": "POST"
    }
    return jsonify(metadata)

@app.route('/predict', methods=['POST'])
def predict():
    """Receives encrypted data and evaluation keys, returns encrypted prediction."""
    try:
        encrypted_data_b64 = request.data
        serialized_evaluation_keys_b64 = request.headers.get('Evaluation-Keys')

        if not encrypted_data_b64:
            return jsonify({"error": "Missing encrypted data in request body"}), 400
        if not serialized_evaluation_keys_b64:
            return jsonify({"error": "Missing 'Evaluation-Keys' header"}), 400

        encrypted_data = base64.b64decode(encrypted_data_b64)
        serialized_evaluation_keys = base64.b64decode(serialized_evaluation_keys_b64)
        encrypted_result = server.run(encrypted_data, serialized_evaluation_keys)
        encrypted_result_b64 = base64.b64encode(encrypted_result).decode('utf-8')

        return encrypted_result_b64

    except base64.binascii.Error as e:
        return jsonify({"error": f"Base64 decoding error: {e}"}), 400
    except Exception as e:
        app.logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
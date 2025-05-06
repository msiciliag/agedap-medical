import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_info(self):
        response = requests.get(f"{self.base_url}/info")
        response.raise_for_status()
        return response.json()

    def predict(self, data, eval_keys):
        files = {
            'encrypted_data': ('encrypted_data.bin', data, 'application/octet-stream'),
            'evaluation_keys': ('evaluation_keys.bin', eval_keys, 'application/octet-stream')
        }
        response = requests.post(f"{self.base_url}/predict", files=files)
        response.raise_for_status()
        return response.content
    

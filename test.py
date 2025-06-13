import requests
def test_http_get_endpoint(base_url, endpoint):
    """Attempts to send a GET request to a given endpoint."""
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        if response.ok: # Checks for status codes 200-299
            print(f"Successfully connected to {url}. Status: {response.status_code}")
            # You can print response.json() or response.text if you expect a specific content type
            print(f"Response from {url}: {response.text}...") # Example: print first 100 chars
        else:
            print(f"Connected to {url}, but received status: {response.status_code}. Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"Failed to connect to {url}. Connection error.")
    except requests.exceptions.Timeout:
        print(f"Failed to connect to {url}. Request timed out.")


if __name__ == "__main__":
    localhost = "127.0.0.1"
    ports = [5001, 5002]
    endpoints_to_test = [
        "/omop_requirements",
        "/fhir_requirements",
        "/additional_service_info"
    ]

    for port in ports:
        base_http_url = f"http://{localhost}:{port}"
        print(f"\n--- Testing HTTP GET endpoints on {base_http_url} ---")
        for endpoint in endpoints_to_test:
            test_http_get_endpoint(base_http_url, endpoint)
import requests
import json

# Constants
FETCH_URL = "http://localhost:5001/fetch"
LOAD_DB_URL = "http://localhost:5001/load-db"
JAEGER_API_URL = "http://localhost:16686/api/traces"

def send_requests():
    for _ in range(100):
        # Send requests to the /fetch endpoint
        fetch_response = requests.get(FETCH_URL)
        print("Fetch status:", fetch_response.status_code)

        # Send requests to the /load-db endpoint
        load_db_response = requests.get(LOAD_DB_URL)
        print("Load DB status:", load_db_response.status_code)

def get_traces():
    # Fetch traces from Jaeger
    params = {
        'service': 'unknown_service',  # Change this to your actual service name used in tracing
    }
    response = requests.get(JAEGER_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch traces from Jaeger:", response.status_code)
        return None

def save_traces(traces):
    if traces:
        # Save the traces to a file
        with open('trace.json', 'w') as f:
            json.dump(traces, f)
        print("Traces saved to trace.json")
    else:
        print("No traces to save.")

if __name__ == "__main__":
    send_requests()
    traces = get_traces()
    save_traces(traces)

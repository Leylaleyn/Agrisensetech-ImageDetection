import requests

def send_post_request(api_url, data, timeout=100):
    try:
        response = requests.post(api_url, json=data, timeout=timeout)
        if response.status_code == 200:
            print(f"[INFO] Data sent successfully.")
        else:
            print(f"[ERROR] Failed to send data. Status code: {response.status_code}")


    except requests.exceptions.Timeout:
        print(f"[ERROR] Connection to {api_url} timed out.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] An error occurred: {e}")



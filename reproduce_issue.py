import requests
import json

url = 'http://127.0.0.1:5001/api/analyze_product'
data = {'product_name': 'sephora lipstick'}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=data, headers=headers)
    with open('response_output.txt', 'w') as f:
        f.write(response.text)
    print(f"Status Code: {response.status_code}")
    print(f"Response written to response_output.txt")
except Exception as e:
    print(f"Error: {e}")

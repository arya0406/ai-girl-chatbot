import requests
import json

# Test the root endpoint
print("Testing root endpoint...")
try:
    response = requests.get("http://localhost:8000/")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")

# Test the chat endpoint
print("\nTesting chat endpoint...")
try:
    data = {"message": "Hello"}
    response = requests.post("http://localhost:8000/chat", json=data)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.text}")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")

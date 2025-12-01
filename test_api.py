import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

USERNAME = 'testing'
PASSWORD = 'testing'

print("Testing movie API\n")

print("Step 1: retreiving token...")
response = requests.post(f'{BASE_URL}/token',
                        json={'username': USERNAME, 'password': PASSWORD})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

token = response.json()['token']
headers = {'Authorization': f'Bearer {token}'}

# GET movies
print("step 2: retreiving all movies...")
response = requests.get(f'{BASE_URL}/movies', headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# POST new movie
print("Step 3: adding new movie...")
new_movie = {'name': 'Inception', 'year': 2010, 'oscars': 4}
response = requests.post(f'{BASE_URL}/movies', headers=headers, json=new_movie)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

print("It works")
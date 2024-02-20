import requests
from flask import request, jsonify

def call_put(project_id):
    url = f'http://127.0.0.1:5000/nobatek/put_ensnaredata/{project_id}'
    response = requests.put(url)
    print(response.json())

    with open('api-response.json', 'r') as file:
        data = file.read()
        print(data)


if __name__ == "__main__":
    call_put(1006)

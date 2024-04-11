# TODO : Remove this file after testing

import requests

if __name__ == "__main__":
    try:
        # Check the config.py file to get the right credentials

        # ----------------------------------- USER ----------------------------------- #

        response = requests.post('http://127.0.0.1:5000/create_user/susan/beauty/user', auth=('john', 'hello'))
        print(response.json())
        #response = requests.delete('http://127.0.0.1:5000/delete_user/ben', auth=('john', 'hello'))
        #response = requests.put('http://127.0.0.1:5000/update_user/ben/chicken/admin', auth=('john', 'hello'))
        #response = requests.get('http://127.0.0.1:5000/get_users', auth=('john', 'hello'))

        # ----------------------------------- DATA ----------------------------------- #

        print("TEST 1: create a new project")
        # response = requests.post('http://127.0.0.1:5000/project/1006', auth=('john', 'hello'))
        #response = requests.get('http://127.0.0.1:5000/nobatek/get_data/1006', auth=('john', 'hello'))
        print(response.json())

        resp = requests.get('http://127.0.0.1:5000/scenarios/1234', auth=('john', 'hello'))
        print(resp.json())
        print('---------------------')
        resp = requests.get('http://127.0.0.1:5000/scenarios/1234', auth=('susan', 'beauty'))
        print(resp.json())

        resp = requests.delete('http://127.0.0.1:5000/project/1234', auth=('susan', 'beauty'))
    except Exception as e:
        print(str(e))
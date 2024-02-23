# TODO : Remove this file after testing

import requests

if __name__ == "__main__":
    try:
        # Check the config.py file to get the right credentials

        # ----------------------------------- USER ----------------------------------- #

        #response = requests.post('http://127.0.0.1:5000/nobatek/create_user/ben/pass/user', auth=('john', 'hello'))
        #response = requests.delete('http://127.0.0.1:5000/nobatek/delete_user/ben', auth=('john', 'hello'))
        #response = requests.put('http://127.0.0.1:5000/nobatek/update_user/ben/chicken/admin', auth=('john', 'hello'))
        #response = requests.get('http://127.0.0.1:5000/nobatek/get_users', auth=('john', 'hello'))

        # ----------------------------------- DATA ----------------------------------- #

        response = requests.post('http://127.0.0.1:5000/nobatek/insert_data/1006', auth=('john', 'hello'))
        #response = requests.get('http://127.0.0.1:5000/nobatek/get_data/1006', auth=('john', 'hello'))
        print(response.json())
    except Exception as e:
        print(str(e))
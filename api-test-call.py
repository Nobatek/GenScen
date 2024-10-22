# TODO : Remove this file after testing

import requests

def _test_users():
    print('Create user')
    response = requests.post('http://127.0.0.1:5000/create_user/tecnalia/fake/user', auth=('john', 'hello'))
    print(response.json())
    response = requests.delete('http://127.0.0.1:5000/delete_user/ben', auth=('john', 'hello'))
    print(response.json())
    response = requests.put('http://127.0.0.1:5000/update_user/ben/chicken/admin', auth=('john', 'hello'))
    print(response.json())
    response = requests.get('http://127.0.0.1:5000/get_users', auth=('john', 'hello'))
    print(response.json())

    print('Create user')
    response = requests.post('http://127.0.0.1:5000/create_user/fdfd/uytyu/user', auth=('tecnalia', 'fake'))
    print(response.json())


def _test_projects():
    try:
        #print('Test from Tecnalia')
        response = requests.post('https://genscen.ensnare.nobatek.com/project/1047', auth=('pierre', 'ensn@re'))
        print(response.json())

        response = requests.get('https://genscen.ensnare.nobatek.com/scenarios/1047', auth=('pierre', 'ensn@re'))
        #response = requests.get('http://127.0.0.1:5000/scenarios/1047', auth=('john', 'hello'))
        print(response.json())

        response = requests.delete('https://genscen.ensnare.nobatek.com/project/1047', auth=('pierre', 'ensn@re'))
        print(response.json())

        # print("TEST 1: create a new project")
        #response = requests.post('http://127.0.0.1:5000/project/1006', auth=('john', 'hello'))
        #print(response.json())
        #response = requests.get('http://127.0.0.1:5000/scenarios/1006', auth=('john', 'hello'))
        #print(response.json())

        #resp = requests.get('http://127.0.0.1:5000/scenarios/1234', auth=('john', 'hello'))
        #print(resp.json())
        #print('---------------------')
        #resp = requests.get('http://127.0.0.1:5000/scenarios/1234', auth=('susan', 'beauty'))
        #print(resp.json())

        #resp = requests.delete('http://127.0.0.1:5000/project/1234', auth=('susan', 'beauty'))
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    # _test_users()
    _test_projects()
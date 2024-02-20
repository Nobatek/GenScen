from hashlib import sha512
import time
import base64
import requests
import flask
from flask import request, jsonify


app = flask.Flask(__name__)
app.config["DEBUG"] = True


def to_native_string(string, encoding="ascii"):
    """Given a string object, regardless of type, returns a representation of
    that string in the native string type, encoding and decoding where
    necessary. This assumes ASCII unless told otherwise.
    """
    if isinstance(string, str):
        out = string
    else:
        out = string.decode(encoding)

    return out


def get_technalia_data(project_id):
    # Using hashlib.sha512() method
    params = {"project_id": str(project_id), "param_name":"longitude"}
    prehash = sha512(str(params).encode('utf-8')).hexdigest()
    # hash = SHA512(timestamp$url$user$prehash$pass)
    now = str(time.time())[:13]
    core_url = 'ensnare.tecnalia.com'
    url = 'https://'+core_url+'/DP4ER/webresources/frontend/ensnare_ddbb/get_project_param'
    url2 = 'https://'+core_url+'/DP4ER/webresources/frontend/ensnare_ddbb/get_scengen_params?project_id='+str(project_id)
    user = 'guest@guest.com'
    passwd = ''

    hash_auth = sha512(str(now+'$'+core_url+'$'+user+'$'+prehash+'$'+passwd).encode('utf-8')).hexdigest()
    basic_auth = 'Basic ' + to_native_string(base64.b64encode(bytes(user + " : " + hash_auth, 'utf-8'))).strip()

    headers = {'Content-Type': 'application/json', 'Authorization': basic_auth, 'Timestamp':  now}
    res = requests.get(url2, params=params, headers=headers)

    if res.status_code == 200:
        return res.content
    else:
        switch = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
            503: "Service Unavailable"
        }

        return switch.get(res.status_code, "Unknown Error")


# ------------------------------------------------------------------------------------------------ #
#                                             API CALLS                                            #
# ------------------------------------------------------------------------------------------------ #


@app.route('/nobatek/put_ensnaredata/<int:project_id>', methods=['PUT'])
def put_data(project_id):
    data = get_technalia_data(project_id)

    # TODO: UPDATE .TTL FILE

    try:
        with open('api-response.json', 'w') as file:
            file.write(data.decode('utf-8'))

        return jsonify({'message': 'Data successfully updated!'})
    except Exception as e:
        return jsonify({data: str(e)})


if __name__ == '__main__':
    app.run(debug=True)
from hashlib import sha512
import time
import base64
import requests
import flask
from flask import jsonify
from extract import insert_data
from flask_httpauth import HTTPBasicAuth


app = flask.Flask(__name__)
app.config["DEBUG"] = True
auth = HTTPBasicAuth()


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

    headers = {'Content-Type': 'application/json', 'Authorization': basic_auth, 'Timestamp': now}
    res = requests.get(url2, params=params, headers=headers)

    if res.status_code == 200:
        return res.json()
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

@auth.verify_password
def verify_password(username, password):
    if username == 'your_username' and password == 'your_password':
        return True
    return False

@app.route('/nobatek/post_ensnaredata/<int:project_id>', methods=['POST'])
def post_data(project_id):
    try:
        data = get_technalia_data(project_id)
        insert_data(data)
        return jsonify({"status": "success", "message": "Data inserted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/tecnalia/<int:project_id>', methods=['GET'])
@auth.login_required
def get_data(project_id):
    return get_technalia_data(project_id)

if __name__ == '__main__':
    app.run(debug=True)
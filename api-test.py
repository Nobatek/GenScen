from hashlib import sha512
import time
import base64
import requests
from flask import Flask, jsonify, g
from extract import insert_data
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import USERS

from extract import get_baseline, get_nZeB, get_Ensnare_Passive, remove_data


# App configuration
app = Flask(__name__)
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


def get_tecnalia_data(project_id):
    # Using hashlib.sha512() method
    params = {"project_id": str(project_id), "param_name":"longitude"}
    prehash = sha512(str(params).encode('utf-8')).hexdigest()
    # hash = SHA512(timestamp$url$user$prehash$pass)
    now = str(time.time())[:13]
    core_url = 'ensnare.tecnalia.com'
    # url = 'https://'+core_url+'/DP4ER/webresources/frontend/ensnare_ddbb/get_project_param'
    url2 = 'https://'+core_url+'/DP4ER/webresources/frontend/ensnare_ddbb/get_genscen_params?project_id='\
           + str(project_id)
    user = 'guest@guest.com'
    passwd = ''

    hash_auth = sha512(str(now+'$'+core_url+'$'+user+'$'+prehash+'$'+passwd).encode('utf-8')).hexdigest()
    basic_auth = 'Basic ' + to_native_string(base64.b64encode(bytes(user + " : " + hash_auth, 'utf-8'))).strip()

    headers = {'Content-Type': 'application/json', 'Authorization': basic_auth, 'Timestamp': now}
    res = requests.get(url2, params=params, headers=headers)

    # Manage the response
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


# ---------------------------------------------------------------------------- #
#                                      API                                     #
# ---------------------------------------------------------------------------- #


# ---------------------------------- AUTHENTICATION ---------------------------------- #

"""
    @brief : Verify the password
    @param : username : string : The username
    @param : password : string : The password
    @return : bool : The status of the password
"""
@auth.verify_password 
def verify_password(username, password): 
    user = USERS.get(username)
    if user and check_password_hash(user.get('password'), password): 
        g.user = username 
        return True
    return False


"""
    @brief : Error handler for the authentication
    @return : json : The status of the request
"""
@auth.error_handler
def unauthorized():
    return jsonify({"status": "error", "message": "Wrong username or password"}), 401


# Now we can use @role_required(['admin']) or @role_required(['user']) to protect the routes
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user and USERS.get(g.user).get('role') in roles:
                return f(*args, **kwargs)
            else:
                return jsonify(
                    {"status": "error", "message": "You do not have permission to access this resource"}), 403
        return decorated_function
    return decorator


# ---------------------------------- ROUTES ---------------------------------- #

"""
    @brief : Get the data from the Tecnalia API and insert it into the database
    @param : project_id : int : The project id
    @return : json : The status of the request
"""
@app.route('/project/<int:project_id>', methods=['POST'])
@auth.login_required
@role_required(['admin', 'user'])
def post_data(project_id):
    try:
        print("Get data from Tecnalia")
        data = get_tecnalia_data(project_id)
        res = insert_data(data)
        if res == 200:
            return jsonify({"status": "success", "message": "Data inserted successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Data not inserted"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


"""
    @brief : Get the data from the database
    @param : project_id : int : The project id
    @return : json : The data from the tecnalia database
"""
@app.route('/scenarios/<int:project_id>', methods=['GET'])
@auth.login_required
@role_required(['admin', 'user'])
def get_scenarios(project_id):
    result = dict(**get_baseline(project_id), **get_nZeB(project_id), **get_Ensnare_Passive(project_id))
    return jsonify(result), 200


"""
    @brief : Remove project from the database
    @return : json : The HTTP response
"""
@app.route('/project/<int:project_id>', methods=['DELETE'])
@auth.login_required
@role_required(['admin', 'user'])
def remove(project_id):
    return jsonify(remove_data(project_id), 200)


# ------------------------------ USER MANAGEMENT ----------------------------- #

"""
    @brief : Create a new user
    @param : username : string : The username
    @param : password : string : The password
    @param : role : string : The role
    @return : json : The status of the request
"""
@app.route('/create_user/<string:username>/<string:password>/<string:role>', methods=['POST'])
@auth.login_required
@role_required(['admin'])
def create_user(username, password, role):
    try:
        if username in USERS:
            return jsonify({"status": "error", "message": "User already exists"}), 400
        hashed_password = generate_password_hash(password)
        USERS[username] = {'password': hashed_password, 'role': role}
        with open('config.py', 'w') as file:
            file.write("USERS = " + str(USERS))
        return jsonify({"status": "success", "message": "User created successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


"""
    @brief : Delete a user
    @param : username : string : The username
    @return : json : The status of the request
"""
@app.route('/delete_user/<string:username>', methods=['DELETE'])
@auth.login_required
@role_required(['admin'])
def delete_user(username):
    try:
        if username not in USERS:
            return jsonify({"status": "error", "message": "User does not exist"}), 400
        USERS.pop(username)
        with open('config.py', 'w') as file:
            file.write("USERS = " + str(USERS))
        return jsonify({"status": "success", "message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    

"""
    @brief : Update a user
    @param : username : string : The username
    @param : password : string : The password
    @param : role : string : The role
    @return : json : The status of the request
"""
@app.route('/update_user/<string:username>/<string:password>/<string:role>', methods=['PUT'])
@auth.login_required
@role_required(['admin'])
def update_user(username, password, role):
    try:
        hashed_password = generate_password_hash(password)
        USERS[username] = {'password': hashed_password, 'role': role}
        with open('config.py', 'w') as file:
            file.write("USERS = " + str(USERS))
        return jsonify({"status": "success", "message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    

"""
    @brief : Get all the users
    @return : json : The users
"""
@app.route('/get_users', methods=['GET'])
@auth.login_required
@role_required(['admin'])
def get_users():
    return jsonify(USERS)


if __name__ == '__main__':
    app.run(debug=True)
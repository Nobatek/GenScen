from hashlib import sha512
import time
import base64
import requests

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

# Using hashlib.sha512() method
params = {"project_id": 1006, "param_name":"longitude"}
prehash = sha512(str(params).encode('utf-8')).hexdigest()
# hash = SHA512(timestamp$url$user$prehash$pass)
now = str(time.time())[:13]
core_url = 'ensnare.tecnalia.com'
url = 'https://'+core_url+'/DP4ER/webresources/frontend/ensnare_ddbb/get_project_param'
url2 = 'https://'+core_url+'/DP4ER/webresources/frontend/ensnare_ddbb/get_scengen_params?project_id=1006'
user = 'guest@guest.com'
passwd = ''

hash_auth = sha512(str(now+'$'+core_url+'$'+user+'$'+prehash+'$'+passwd).encode('utf-8')).hexdigest()
basic_auth = 'Basic ' + to_native_string(base64.b64encode(bytes(user + " : " + hash_auth, 'utf-8'))).strip()

headers = {'Content-Type': 'application/json', 'Authorization': basic_auth, 'Timestamp':  now}
res = requests.get(url2, params=params, headers=headers)
print(res.content)

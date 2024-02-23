#!/usr/bin/python3

import os
import sys
import json

from extract import get_baseline, get_nZeB, get_Ensnare_Passive, remove_data

#def _upload_to_jena(self, pathfile):
#    ttl_data = open(pathfile).read()
#    headers = {'Content-Type': 'text/turtle;charset=utf-8'}
#    r = requests.post('http://localhost:3030/GenScen?default', data=ttl_data, headers=headers)
#    if r.status_code != 200:
#        raise Exception("Cannot access triple store while trying to load data!")

def _check_java():
    return os.system("java --version") == 0

# def _clean_json(json_data):
#     dict_out = {}
#     for k in json_data.keys():
#         if k in ["datatype", "type"]:
#             continue
#         elif k == "value":
#             return json_data[k]
#         elif isinstance(json_data[k], list) :
#             dict_out[k] = [_clean_json(data) for data in json_data[k]]
#         else:
#             dict_out[k] = _clean_json(json_data[k])
#     return dict_out
#
# def _save_to_file(file_name, dict_data):
#     pre, _ = os.path.splitext(file_name)
#     # JSON FILE
#     with open(pre + ".json", "w") as outfile:
#         json.dump(dict_data, outfile, indent=4)

def main():
    print('----- EXTRACTING DATA----')
    result = dict(**get_baseline(1234), **get_nZeB(1234), **get_Ensnare_Passive(1234))
    print(json.dumps(result))

    remove_data(1234)
    result = dict(**get_baseline(1234), **get_nZeB(1234), **get_Ensnare_Passive(1234))
    print(json.dumps(result))


if __name__ == '__main__':
    if len(sys.argv) != 1:
        sys.exit('No argument needed')
    if not _check_java():
        sys.exit('Java does not seem to be installed')
    sys.exit(main())  # next section explains the use of sys.exit

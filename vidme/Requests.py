
from requests import get, post

API_URL = "https://api.vid.me"

def do_request(uri, token=None, method='POST', extraheaders=None, **kwargs):    
    headers = {}

    headers['Authorization'] = "Basic Zm9vOmJhcg=="

    if extraheaders is not None:
        headers.update(extraheaders)
    if token is not None:
        headers['AccessToken'] = token
 
    func = post

    if method == 'POST':
        func = post
    elif method == 'GET':
        func = get
 
    result = func(API_URL + uri, headers=headers, **kwargs)
 
    result_json = result.json()

    if result.status_code >= 400:
        if result_json['code'] != "internal_server_error":
            print "request failed!", result_json['code'], result_json['error']
        return False
 
    if result_json is None or not 'status' in result_json or result_json['status'] is False:
        print 'request failed!!', result_json['code'], result_json['error']
        return False

    return result_json

def request(*args, **kwargs):
    return do_request(*args, **kwargs)

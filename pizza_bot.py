import json
import os
import requests

def open_json(json_path):
    with open(json_path, "r") as fp:
        json_doc = fp.read()
    doc = json.loads(json_doc)
    print(doc)


def get_access_token(redis_call):
    if redis_call.get('access_token'):
        access_token = redis_call.get('access_token').decode('utf-8')
    else:
        url = 'https://api.moltin.com/oauth/access_token'
        params = {'client_id': os.getenv('CLIENT_ID'),
                  'client_secret': os.getenv('CLIENT_SECRET'),
                  'grant_type': 'client_credentials'
                  }
        response = requests.post(url, data=params)
        response.raise_for_status()
        token_info = response.json()
        access_token = f'''Bearer {token_info['access_token']}'''
        expires = token_info['expires_in']
        redis_call.set('access_token',
                       access_token,
                       ex=expires)
    return access_token


if __name__ == "__main__":
    menu_path = "./menu.json"
    address_path = "./addresses.json"
    
    data = {
    'client_id': 'xCVYa8wHn831uF75QjGdijtDN3ZnglpR6lFrhbLK6v',
    'grant_type': 'implicit',}

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    resp_j = response.json()
    print(resp_j['access_token'])
    ##open_json(menu_path)
    ##open_json(address_path)

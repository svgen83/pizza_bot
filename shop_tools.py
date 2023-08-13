import json
import os
import requests
from dotenv import load_dotenv
from pprint import pprint


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


def create_product(access_token, product):
    headers = {'Authorization': f'Bearer {access_token}'}

    json_data = {'data': {
        'type': 'product',
        'attributes': {
            'name': product['name'],
            'sku': str(product['id']),
            'slug': str(product['id']),
            'description': product['description'],
            'status': 'live',
            'commodity_type': 'physical'},
        },}

    response = requests.post(
    'https://api.moltin.com/pcm/products',
    headers=headers, json=json_data)
    response.raise_for_status()
    product_id = response.json()['data']['id']
    return product_id

def load_image(access_token, image_url):
    
    headers = {
    'Authorization': f'Bearer {access_token}'}
    files = {'file_location': (None, image_url)}
    response = requests.post(
        'https://api.moltin.com/v2/files',
        headers=headers, files=files)
    response.raise_for_status()
    return response.json()['data']['id']


##def create_product_v2(access_token):
##    headers = {'Authorization': f'Bearer {access_token}',
##               'Content-Type': 'application/json'
##               }
##    params = {'data': {
##        'type': 'product',
##        'name': 'pizza',
##        'slug': 'pizza',
##        'sku': '3',
##        'manage_stock': False,
##        'description': 'no description',
##        'price': [{'amount': 800,
##                   'currency': 'RUB',
##                   "includes_tax": True}],
##        "status": 'live',
##        'commodity_type': 'physical'
##    }}
##    response = requests.post('https://api.moltin.com/v2/products',
##                             headers=headers,
##                             json=params)
##    response.raise_for_status()
##    print(response.json())


def create_main_image(access_token, file_id, product_id):
    headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'}

    json_data = {
        'data': {
            'type': 'file',
            'id': file_id}}

    response = requests.post(
        f'https://api.moltin.com/pcm/products/{product_id}/relationships/main_image',
        headers=headers,
        json=json_data)
    response.raise_for_status()
    print(response.status_code)


def create_price_book(access_token):
    headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'}

    json_data = {
        'data': {
            'type': 'pricebook',
            'attributes': {
                'name': 'Pizza_shop',
                'description': 'за 1 штуку'},},}
    response = requests.post(
        f'https://api.moltin.com/pcm/pricebooks',
        headers=headers,
        json=json_data)
    response.raise_for_status()
    return(response.json()['data']['id'])


def create_product_price(access_token, price_book_id, product):
    headers = {
        'Authorization': f'Bearer {access_token}',
        #'Content-Type': 'application/json'
        }
    json_data = {
        'data':{
            'type': 'product-price',
            'attributes': {
                'sku': str(product['id']),
                'currencies': {'RUB': {
                    'amount': product['price'],
                    'tiers': {},
                    'includes_tax': False},
                               }}}}
    
    response = requests.post(
        f'https://api.moltin.com/pcm/pricebooks/{price_book_id}/prices',
        headers=headers,
        json=json_data)
    response.raise_for_status()


def create_flow(access_token, flow_model):
    fields = {'address': 'string',
              'alias': 'string',
              'longitude': 'float',
              'latitude': 'float'}
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'}
    json_data = {
        'data': {'type': 'flow',
                 'name': flow_model,
                 'slug': flow_model,
                 'description': 'Магазин пиццерия',
                 'enabled': True},}
    response = requests.post(
        'https://api.moltin.com/v2/flows',
        headers=headers, json=json_data)
    response.raise_for_status()
    #print(response.json())
    flow = response.json()['data']
    flow_id = flow['id']
    for field_name, field_type in fields.items():
        create_field(flow_id, field_name, field_type, access_token=access_token)


def create_field(flow_id, field_name, field_type, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'}

    json_data = {
        "data": {
        "type": "field",
        "name": field_name,
        "slug": field_name,
        "field_type": field_type,
        "required": True,
        "enabled": True,
        "description": "",
        "relationships": {
            "flow": {
                "data": {
                    "type": "flow",
                    "id": flow_id
                }}}}}

    response = requests.post(
        'https://api.moltin.com/v2/fields',
        headers=headers, json=json_data)
    response.raise_for_status()
    print(response.json())
 

if __name__ == "__main__":

    load_dotenv()
##    menu_path = "./menu.json"
##    address_path = "./addresses.json"
    menu_url = 'https://dvmn.org/media/filer_public/a2/5a/a25a7cbd-541c-4caf-9bf9-70dcdf4a592e/menu.json'
    
    address_url = 'https://dvmn.org/media/filer_public/90/90/9090ecbf-249f-42c7-8635-a96985268b88/addresses.json'
      
    data = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'grant_type': 'client_credentials'}

    token_response = requests.post(
    'https://api.moltin.com/oauth/access_token', data=data)
    token_response.raise_for_status()
    token = token_response.json()['access_token']

    #price_book_id = create_price_book(token)

    #menu_response = requests.get(menu_url)
    #menu_response.raise_for_status()
    #pizza_menu = menu_response.json()
    #for pizza in pizza_menu:
     #   product_id = create_product(token, pizza)
      #  create_product_price(token, price_book_id, pizza)
      #  main_image_id = load_image(token, pizza['product_image']['url'])
       # create_main_image(token, main_image_id, product_id)
    #print("Товары добавлены")
    
    
    address_response = requests.get(address_url)
    address_response.raise_for_status()
    pizzeria_adresses = address_response.json()
    create_flow(token, 'Pizzerias')
    
    

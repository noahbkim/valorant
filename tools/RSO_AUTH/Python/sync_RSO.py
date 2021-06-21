import requests
import re

def authorize(username, password):
    session = requests.session()
    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/opt_in',
        'response_type': 'token id_token',
    }
    r = session.post('https://auth.riotgames.com/api/v1/authorization', json=data)

    data = {
        'type': 'auth',
        'username': username,
        'password': password
    }
    r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data)
    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    try:
        data = pattern.findall(r.json()['response']['parameters']['uri'])[0]
        access_token = data[0]
        expires_in = data[2]
    except KeyError:
        raise ValueError("Invalid Username or Password passed!")

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
    json_data = r.json()
    entitlements_token = json_data['entitlements_token']

    r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})
    json_data = r.json()
    user_id = json_data['sub']
    
    session.close()
    return [access_token, entitlements_token, user_id, expires_in]

if __name__ == "__main__":
    USERNAME = input("Enter username: ")
    PASSWORD = input("Enter password: ")
    print()
    try:
        result = authorize(USERNAME, PASSWORD)
        access_token = result[0]
        entitlements_token = result[1]
        user_id = result[2]
        expire = result[3]

        print("access_token => Bearer " + access_token)
        print()
        print("entitlements_token => " + entitlements_token)
        print()
        print("user_id => " + user_id)
        print()
        print("Token_expire_time => " + expire)
        
    except ValueError:
        print("Incorrect Username or Password")
    
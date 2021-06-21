
################# CODE FROM LUC1412 SLIGHTLY MODIFIED #############
#                                                                  
# https://gist.github.com/Luc1412/1f93257a2a808679ff014f258db6c35b 
#                                                                  
###################################################################


import asyncio
import aiohttp
import re

async def authorize(username, password):
    session = aiohttp.ClientSession()
    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/opt_in',
        'response_type': 'token id_token',
    }
    await session.post('https://auth.riotgames.com/api/v1/authorization', json=data)

    data = {
        'type': 'auth',
        'username': username,
        'password': password
    }
    async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data) as resp:
        json_data = await resp.json()
    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    try:
        data = pattern.findall(json_data['response']['parameters']['uri'])[0]
        access_token = data[0]
        expires_in = data[2]
    except KeyError:
        raise ValueError("Invalid Username or Password passed!")

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as resp:
        json_data = await resp.json()
    entitlements_token = json_data['entitlements_token']

    async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as resp:
        json_data = await resp.json()   
    user_id =  json_data['sub']

    await session.close()
    return [access_token, entitlements_token, user_id, expires_in]
    

if __name__ == '__main__':
    USERNAME = input("Enter username: ")
    PASSWORD = input("Enter password: ")
    print()
    try:
        result = asyncio.get_event_loop().run_until_complete(authorize(USERNAME, PASSWORD))
        access_token = result[0]
        entitlements_token = result[1]
        user_id = result[2]
        expire = result[3]

        print("Access_token => Bearer " + access_token)
        print()
        print("Entitlements_token => " + entitlements_token)
        print()
        print("User_id => " + user_id)
        print()
        print("Token_expire_time => " + expire)
        
    except ValueError:
        print("Incorrect Username or Password")
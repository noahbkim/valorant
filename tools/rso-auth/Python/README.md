# RSO_AUTH

This tool facilitates in retreving user tokens to access RiotClient endpoints.
It is targeted at Python 3.6 and above.

## Examples

You can use either async_RSO or sync_RSO to make requests to the Riot Authentication services.
Only difference between async_RSO and sync_RSO is the speed, async_RSO is faster than sync_RSO.
To run this tool use (we will use async_RSO here) :

```commandline
$ python3 async_RSO.py
Enter username: USERNAME
Enter password: PASSWORD

Access_token => Bearer <TOKEN>

Entitlements_token => <TOKEN>

User_id => <USER_ID>

Token_expire_time => 3600 
```

### Contact

If you face any problems please join the unofficial Valorant app developer [Discord](https://discord.gg/42ntAKCBku) or make an issue in this repository [Create issue](https://github.com/noahbkim/valorant/issues/new)

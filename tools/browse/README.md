# Browser

This tool facilitates API endpoint discovery and testing.
It is targeted at Python 3.9, but may work with prior version that support f-strings and type annotations.

## Examples

You can use browse to make requests to the local Riot client instance.
For example, you can ask for the currently authenticated user's API credentials.
This requires Valorant to be running:

```commandline
$ python3.9 browse.py client /entitlements/v1/token
vary: origin
cache-control: no-store
content-length: 1641
content-type: application/json
access-control-allow-origin: http://127.0.0.1:60637
access-control-expose-headers: content-length
{
  "accessToken": "<hex encoded JWT, omitted for security>",
  "entitlements": [],
  "issuer": "https://entitlements.auth.riotgames.com",
  "subject": "<authenticated player PUUID>",
  "token": "<hex encoded JWT, omitted for security>"
}
```

The response headers are written to `stderr` while the body is written to `stdout`.
Consequently, you can pipe just the response body to a separate file if you'd like to look with a separate tool:

```commandline
$ python3.9 browse.py client /entitlements/v1/token > response.json
vary: origin
cache-control: no-store
content-length: 1641
content-type: application/json
access-control-allow-origin: http://127.0.0.1:60637
access-control-expose-headers: content-length
```

Now, the response body can be found in `./response.json`.

# /entitlements/v1/token

This Riot client endpoint can be used to obtain Valorant API credentials.
An example response consists of the following headers:

```
vary: origin
cache-control: no-store
content-length: 1641
content-type: application/json
access-control-allow-origin: http://127.0.0.1:60637
access-control-expose-headers: content-length
```

The response will also contain this data:

```json
{
  "accessToken": "<hex encoded JWT, omitted for security>",
  "entitlements": [],
  "issuer": "https://entitlements.auth.riotgames.com",
  "subject": "<authenticated player PUUID>",
  "token": "<hex encoded JWT, omitted for security>"
}
```

## Usage

To be able to access Valorant API's, use the data in the received payload to populate the following headers:

- `Authorization`: `Bearer <accessToken>`
- `X-Riot-Entitlements-JWT`: `<token>`

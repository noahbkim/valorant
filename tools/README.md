# Tools

This directory contains user-submitted scripts that can help reverse-engineer the systems surrounding Valorant.
Please make sure to license code snippets you upload.
You can find common open source licenses here: https://choosealicense.com/licenses/.

## Browse

Use [`browse.py`](./browse) to make requests to the local Riot client as well as the Valorant API's.
The command line utility provides a convenient way to pipe the resulting body to a file.
For example:

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

$ python3.9 browse.py client /entitlements/v1/token > response.json
vary: origin
cache-control: no-store
content-length: 1641
content-type: application/json
access-control-allow-origin: http://127.0.0.1:60637
access-control-expose-headers: content-length
# response is written to ./response.json
```

## Logger

The [`logger.py`](./logger) tool allows you parse through Valorant log files.
You can also watch the log file for live updates while the game is running and filter messages by substring:

```commandline
$ python3.9 logger.py --watch
# log is printed, logger waits for new entries to print theme.

$ python3.9 logger.py --watch --filter "https://"
# only messages that contain HTTPS URLs are logged
```

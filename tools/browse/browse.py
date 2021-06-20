"""Valorant API Browser

This module can be used to do testing on Riot client and Valorant API
endpoints. Examples are included in the README.

This module is written for Python 3.9+. Requires requests.s
"""

import os
import sys
import json
import requests
import base64
import urllib.parse

from pathlib import Path
from dataclasses import dataclass


class URL:
    RIOT_AUTHORIZATION = "https://auth.riotgames.com/api/v1/authorization"
    RIOT_TOKEN_ENTITLEMENTS = "https://entitlements.auth.riotgames.com/api/token/v1"
    RIOT_USER_INFO = "https://auth.riotgames.com/userinfo"

    # TODO: support more than just NA lol
    RIOT_GLZ = "https://glz-na-1.na.a.pvp.net"
    RIOT_PD = "https://pd.na.a.pvp.net"


@dataclass
class Lockfile:
    name: str
    pid: int
    port: int
    password: str
    protocol: str

    DEFAULT_PATH = Path(os.getenv("LOCALAPPDATA"), R"Riot Games\Riot Client\Config\lockfile")

    @classmethod
    def parse(cls, content: str) -> "Lockfile":
        """Parse the contents of a Riot client lockfile."""

        name, pid, port, password, protocol = content.split(":")
        return cls(name=name, pid=int(pid), port=int(port), password=password, protocol=protocol)

    @classmethod
    def read(cls, path: Path) -> "Lockfile":
        """Read a Riot lockfile from a given path."""

        return cls.parse(path.read_text())

    def request(self, path: str, **kwargs) -> requests.Response:
        """Make a request to a path on the Riot client HTTPS API.

        Valorant must be running to make a connection to the local API
        server. Keyword arguments are passed to `requests.get`.
        """

        token = base64.b64encode(("riot:" + self.password).encode()).decode()
        return requests.get(
            f"https://127.0.0.1:{self.port}{path}",
            headers=dict(authorization=f"Basic {token}"),
            verify=False,
            **kwargs)


class RiotApiSession:
    """A session opened against Valorant API servers."""

    session: requests.Session
    puuid: str = None

    def __init__(self):
        self.session = requests.session()

    def login(self, username: str, password: str):
        """Authenticate via username and password.

        This method uses a pretty sketchy facet of the Valorant
        website and is not recommended.
        """

        self.session.post(URL.RIOT_AUTHORIZATION, json={
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token"})
        response = self.session.put(URL.RIOT_AUTHORIZATION, json={
            "type": "auth",
            "username": username,
            "password": password})

        uri = response.json()["response"]["parameters"]["uri"]
        data = urllib.parse.urlparse(uri)
        parameters = urllib.parse.parse_qs(data.fragment)
        access_token = parameters["access_token"][0]
        self.session.headers["Authorization"] = f"Bearer {access_token}"

        response = self.session.post(URL.RIOT_USER_INFO, json={})
        self.puuid = response.json()["sub"]

        response = self.session.post(URL.RIOT_TOKEN_ENTITLEMENTS, json={})
        entitlements_token = response.json()["entitlements_token"]
        self.session.headers["X-Riot-Entitlements-JWT"] = entitlements_token

    def authenticate(self, lockfile: Lockfile, client_platform: str = "platform", client_version: str = "version"):
        """Authenticate from credentials in a lockfile.

        This does not properly set the X-Riot-ClientPlatform and
        X-Riot-ClientVersion correctly. Those fields can be provided
        in the function arguments.
        """

        data = lockfile.request("/entitlements/v1/token").json()
        self.puuid = data["subject"]
        self.session.headers.update({
            'Authorization': f"Bearer {data['accessToken']}",
            'X-Riot-Entitlements-JWT': data['token'],
            'X-Riot-ClientPlatform': client_platform,
            'X-Riot-ClientVersion': client_version})


def print_response(response: requests.Response):
    """Nicely format a response with JSON body."""

    for key, value in response.headers.items():
        print(f"{key}: {value}", file=sys.stderr, flush=True)

    # Print in separate streams so you can pipe data into a file
    if response.headers.get("content-type").lower() == "application/json":
        json.dump(response.json(), fp=sys.stdout, indent=2)
    else:
        print(response.text)


def main():
    """Create an argument parser and run based on options."""

    import argparse
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    parser = argparse.ArgumentParser()
    parser.add_argument("--lockfile", help="provide a custom lockfile path", default=Lockfile.DEFAULT_PATH)
    parser_subparsers = parser.add_subparsers(required=True, dest="mode")

    # Query the Riot client
    lockfile_parser = parser_subparsers.add_parser("client")
    lockfile_parser.add_argument("path")

    # Query Valorant API's
    api_parser = parser_subparsers.add_parser("api")
    api_parser.add_argument("url")

    args = parser.parse_args()

    if args.mode == "client":
        lockfile = Lockfile.read(Path(args.lockfile))
        response = lockfile.request(args.path)
        print_response(response)

    elif args.mode == "api":
        lockfile = Lockfile.read(Path(args.lockfile))
        session = RiotApiSession()
        session.authenticate(lockfile)
        response = session.session.get(args.url)
        print_response(response)


if __name__ == '__main__':
    main()


# def get_current_match_id(self) -> str:
#     print(f"{URL.RIOT_GLZ}/core-game/v1/players/{self.user_id}")
#     response = self.session.get(f"{URL.RIOT_GLZ}/core-game/v1/players/{self.user_id}")
#     print(response.json())
#     return response.json()["MatchID"]
#
# def get_match_pregame(self, match_id: str):
#     response = self.session.get(f"{URL.RIOT_GLZ}/pregame/v1/matches/{match_id}")
#     print(json.dumps(response.json(), indent=2))
#
# def get_match_core(self, match_id: str):
#     print(f"{URL.RIOT_GLZ}/core-game/v1/matches/{match_id}")
#     response = self.session.get(f"{URL.RIOT_GLZ}/core-game/v1/matches/{match_id}")
#     print(json.dumps(response.json(), indent=2))
#     return response.json()
#
# def get_match_details(self, match_id: str):
#     response = self.session.get(f"{URL.RIOT_PD}/match-details/v1/matches/{match_id}")
#     print(response.text)
#     with open("test.json", "w") as file:
#         file.write(json.dumps(response.json(), indent=2))
#     print(json.dumps(response.json(), indent=2))
#
# def get_party_id(self, uid: str):
#     response = self.session.get(f"{URL.RIOT_GLZ}/parties/v1/players/{uid}")
#     print(json.dumps(response.json(), indent=2))
#     return response.json()["CurrentPartyID"]
#
# def get_party(self, party_id: str):
#     response = self.session.get(f"{URL.RIOT_GLZ}/parties/v1/parties/{party_id}")
#     print(f"{URL.RIOT_GLZ}/parties/v1/parties/{party_id}")
#     print(json.dumps(response.json(), indent=2))

"""Valorant API Browser

This module can be used to do testing on Riot client and Valorant API
endpoints. Examples are included in the README.

This module is written for Python 3.9+.
"""

import os
import requests
import base64
import json
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

    @classmethod
    def parse(cls, content: str) -> "Lockfile":
        """Parse the contents of a Riot client lockfile."""

        name, pid, port, password, protocol = content.split(":")
        return cls(name=name, pid=int(pid), port=int(port), password=password, protocol=protocol)

    @classmethod
    def read(cls, path: Path) -> "Lockfile":
        """Read a Riot lockfile from a given path."""

        return cls.parse(path.read_text())

    @classmethod
    def default(cls) -> "Lockfile":
        """Attempt to read the default lockfile path."""

        path = Path(os.getenv("LOCALAPPDATA"), R"Riot Games\Riot Client\Config\lockfile")
        return cls.read(path)

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
    user_id: str = None

    def __init__(self):
        self.session = requests.session()

    def login(self, username: str, password: str):
        self.session.post(URL.RIOT_AUTHORIZATION, json={
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
        })
        response = self.session.put(URL.RIOT_AUTHORIZATION, json={
            "type": "auth",
            "username": username,
            "password": password,
        })
        uri = response.json()["response"]["parameters"]["uri"]
        data = urllib.parse.urlparse(uri)
        parameters = urllib.parse.parse_qs(data.fragment)
        access_token = parameters["access_token"][0]
        self.set_access_token(access_token)

        response = self.session.post(URL.RIOT_USER_INFO, json={})
        self.user_id = response.json()["sub"]

        response = self.session.post(URL.RIOT_TOKEN_ENTITLEMENTS, json={})
        entitlements_token = response.json()["entitlements_token"]
        self.set_entitlements_token(entitlements_token)

    def authenticate(self, lockfile: Lockfile):
        data = lockfile.request("/entitlements/v1/token").json()
        self.user_id = data["subject"]
        self.session.headers.update({
            'Authorization': f"Bearer {data['accessToken']}",
            'X-Riot-Entitlements-JWT': data['token'],
            'X-Riot-ClientPlatform': "platform",
            'X-Riot-ClientVersion': "release"
        })

    def set_access_token(self, token: str):
        print(f"authorization: {token}")
        self.session.headers["Authorization"] = f"Bearer {token}"

    def set_entitlements_token(self, token: str):
        print(f"entitlements: {token}")
        self.session.headers["X-Riot-Entitlements-JWT"] = token

    def get_current_match_id(self) -> str:
        print(f"{URL.RIOT_GLZ}/core-game/v1/players/{self.user_id}")
        response = self.session.get(f"{URL.RIOT_GLZ}/core-game/v1/players/{self.user_id}")
        print(response.json())
        return response.json()["MatchID"]

    def get_match_pregame(self, match_id: str):
        response = self.session.get(f"{URL.RIOT_GLZ}/pregame/v1/matches/{match_id}")
        print(json.dumps(response.json(), indent=2))

    def get_match_core(self, match_id: str):
        print(f"{URL.RIOT_GLZ}/core-game/v1/matches/{match_id}")
        response = self.session.get(f"{URL.RIOT_GLZ}/core-game/v1/matches/{match_id}")
        print(json.dumps(response.json(), indent=2))
        return response.json()

    def get_match_details(self, match_id: str):
        response = self.session.get(f"{URL.RIOT_PD}/match-details/v1/matches/{match_id}")
        print(response.text)
        with open("test.json", "w") as file:
            file.write(json.dumps(response.json(), indent=2))
        print(json.dumps(response.json(), indent=2))

    def get_party_id(self, uid: str):
        response = self.session.get(f"{URL.RIOT_GLZ}/parties/v1/players/{uid}")
        print(json.dumps(response.json(), indent=2))
        return response.json()["CurrentPartyID"]

    def get_party(self, party_id: str):
        response = self.session.get(f"{URL.RIOT_GLZ}/parties/v1/parties/{party_id}")
        print(f"{URL.RIOT_GLZ}/parties/v1/parties/{party_id}")
        print(json.dumps(response.json(), indent=2))

    def get_player_name(self, *player_ids: str):
        response = self.session.put(f"{URL.RIOT_PD}/name-service/v2/players", json=player_ids)
        print(response.json())

    def get_presence(self):
        pass

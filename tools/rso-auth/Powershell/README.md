# Tool Repository

https://github.com/techchrism/riot-token-gen

# Riot Token Generator

A simple way to get a Riot token, entitlement, and user id from a username and password  
Endpoint flow by Luc1412 from https://github.com/RumbleMike/ValorantClientAPI/blob/master/Docs/RSO_AuthFlow.py

# Usage

## Without Saving Project
These will run the script without saving it to disk which is useful for trying the script

### MSHTA
Press `Win` + `r` and enter `mshta https://techchrism.github.io/riot-token-gen/`

### Command
`powershell -Exe Bypass -C "& {((New-Object Net.WebClient).DownloadString('https://techchrism.github.io/riot-token-gen/Riot-Token-CLI.ps1')) | Invoke-Expression}"`

---

## With Saving Project
Download the latest source code zip from releases https://github.com/techchrism/riot-token-gen/releases/ and run `start.bat`

---

## For Developers
The Powershell function to get the Riot token data is in `New-Riot-Token.ps1`

# Sample Run

```
Enter Riot username: my_riot_username
Enter Riot password: *****************

Access Token:
{long string of text}

Entitlement:
{long string of text}

User ID: {user id}
Expires in 3600 seconds
```
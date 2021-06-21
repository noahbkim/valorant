# Tool Repository

https://github.com/techchrism/riot-auth-test

# Riot Auth Test

Hacky project to test stability of generating new tokens from login cookies instead of re-authenticating

### Currently running tests

 - Generating new tokens every 45 minutes from one jar of cookies and
   allowing the set-cookie headers to overwrite the data
 - On another cookie jar, the script is waiting for the main cookies to expire,
   then forcefully setting a new expiration date to see if the expiration is server-side enforced
   
### Observations

So far, this appears to be a reliable method of generating tokens without directly needing the account password.
The default cookie expiration is set for 30 days but this is reset with each token request.
Tests have not yet been running long enough to assess long-term stability.

### Notable Code

The functions `login({username, password}, jar)` and `reauthToken(jar)` are the ones doing the work.

The login function is different from the typical method with the
presence of the `"remember": true` and `"language": "en_US"` elements in the json data. 
These extra elements were observed in a typical web login.
User agent headers are intentionally set to be empty to override
the default "node-fetch" agent which Cloudflare immediately blocks.

`reauthToken` uses behavior observed from Riot websites on different domains.
It grabs the token data from the redirection header.

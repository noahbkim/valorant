################# CODE FROM TECHCHRISM #####################################
#
# https://github.com/techchrism/riot-token-gen/blob/trunk/New-Riot-Token.ps1
#
############################################################################

function New-Riot-Token
{
    <#
    .SYNOPSIS
        Gets a new Riot token for the provided account.
        Includes bearer token, entitlement, and user id
    
    .PARAMETER Username
        The username of the Riot account
    .PARAMETER Password
        The password of the Riot account
    .EXAMPLE
        New-Riot-Token -Username "my_username" -Password "my_password"
    .NOTES
        Author: Techdoodle
        Website: https://techchrism.me
        Endpoint flow by Luc1412 from https://github.com/RumbleMike/ValorantClientAPI/blob/master/Docs/RSO_AuthFlow.py 
    #>

    [CmdletBinding()]
    param (
        [Parameter(Mandatory)] [String] $Username,
        [Parameter(Mandatory)] [SecureString] $Password
    )

    $ProgressPreference = 'SilentlyContinue'

    # Set up cookies for auth request
    Invoke-WebRequest -Uri 'https://auth.riotgames.com/api/v1/authorization' `
                      -Method 'POST' `
                      -ContentType 'application/json' `
                      -Body '{"client_id":"play-valorant-web-prod","nonce":"1","redirect_uri":"https://playvalorant.com/opt_in","response_type":"token id_token"}' `
                      -SessionVariable 'authSession' `
                      -UseBasicParsing `
                       > $null

    $authData = ConvertTo-JSON @{
        'type' = 'auth'
        'username' = $Username
        'password' = ([System.Net.NetworkCredential]::new("", $Password).Password)
    }


    # Perform auth request
    $authBody = Invoke-WebRequest -Uri 'https://auth.riotgames.com/api/v1/authorization' `
                                  -Method 'PUT' `
                                  -ContentType 'application/json' `
                                  -Body $authData `
                                  -WebSession $authSession `
                                  -UseBasicParsing

    # Parse data from auth request to get access token and expiration
    $jsonData = ConvertFrom-JSON $authBody.Content
    if($jsonData.error -eq 'auth_failure')
    {
        throw 'Invalid Riot username or password'
    }
    $queryStr = ([System.Uri] $jsonData.response.parameters.uri).Fragment.Substring(1)
    $parsedQueryStr = [System.Web.HttpUtility]::ParseQueryString($queryStr)
    $accessToken = $parsedQueryStr['access_token']
    $expiration = $parsedQueryStr['expires_in']
    
    # Perform entitlements request
    $entitlementBody = Invoke-WebRequest -Uri 'https://entitlements.auth.riotgames.com/api/token/v1' `
                                         -Method 'POST' `
                                         -Headers @{Authorization = "Bearer $accessToken"} `
                                         -ContentType 'application/json' `
                                         -UseBasicParsing

    # Parse entitlement data
    $entitlementsToken = (ConvertFrom-JSON $entitlementBody.Content).'entitlements_token'


    # Perform user info request
    $userInfoBody = Invoke-WebRequest -Uri 'https://auth.riotgames.com/userinfo' `
                                      -Method 'POST' `
                                      -Headers @{Authorization = "Bearer $accessToken"} `
                                      -ContentType 'application/json' `
                                      -UseBasicParsing

    # Parse user info data
    $userId = (ConvertFrom-JSON $userInfoBody.Content).sub

    return @{
        'accessToken' = $accessToken
        'expiration' = $expiration
        'entitlement' = $entitlementsToken
        'userid' = $userId
    }
}
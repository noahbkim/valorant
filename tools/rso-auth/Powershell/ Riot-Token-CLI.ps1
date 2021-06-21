################# CODE FROM TECHCHRISM #####################################
#
# https://github.com/techchrism/riot-token-gen/blob/trunk/Riot-Token-CLI.ps1
#
############################################################################

. .\New-Riot-Token.ps1

try
{
    $username = Read-Host 'Enter Riot username'
    $password = Read-Host 'Enter Riot password' -AsSecureString

    $tokenData = New-Riot-Token -Username $username -Password $password

    Write-Host ''
    Write-Host 'Access Token:'
    Write-Host $tokenData.accessToken
    Write-Host ''

    Write-Host 'Entitlement:'
    Write-Host $tokenData.entitlement
    Write-Host ''

    Write-Host "User ID: $($tokenData.userid)"
    Write-Host "Expires in $($tokenData.expiration) seconds"
}
catch
{
    Write-Error $_
}

Pause
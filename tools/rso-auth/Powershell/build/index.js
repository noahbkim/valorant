/*
################# CODE FROM TECHCHRISM #################################
#
# https://github.com/techchrism/riot-token-gen/blob/trunk/build/index.js 
#
########################################################################
*/

// Build the powershell into one file
const fs = require('fs').promises;
const path = require('path');

(async () =>
{
    const files = [
        fs.readFile(path.join(__dirname, '..', 'New-Riot-Token.ps1'), 'utf8'),
        fs.readFile(path.join(__dirname, '..', 'Riot-Token-CLI.ps1'), 'utf8'),
        fs.readFile(path.join(__dirname, 'template.hta'), 'utf8'),
    ];
    const [riotTokenFunction, riotTokenCLI, htaTemplate] = await Promise.all(files);

    try
    {
        await fs.mkdir(path.join(__dirname, '..', 'dist'));
    }
    catch(ignored) {}

    const builtScriptText = riotTokenCLI.replace('. .\\New-Riot-Token.ps1', riotTokenFunction);
    const scriptURL = 'https://techchrism.github.io/riot-token-gen/Riot-Token-CLI.ps1';
    const htaText = htaTemplate.replace('{{encoded_data}}',
        Buffer.from(` -Exe Bypass -C "& {((New-Object Net.WebClient).DownloadString('${scriptURL}')) | Invoke-Expression}"`).toString('base64'));

    const outFiles = [
        fs.writeFile(path.join(__dirname, '..', 'dist', 'Riot-Token-CLI.ps1'), builtScriptText, 'utf8'),
        fs.writeFile(path.join(__dirname, '..', 'dist', 'run.hta'), htaText, 'utf8'),
        fs.writeFile(path.join(__dirname, '..', 'dist', 'index.html'), htaText, 'utf8')
    ];
    await Promise.all(outFiles);
})();
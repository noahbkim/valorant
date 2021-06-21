const readline = require('readline');
const Writable = require('stream').Writable;
const winston = require('winston');
const path = require('path');
const fs = require('fs');
const esmImport = require('esm')(module);
const {CookieJar, fetch} = esmImport('node-fetch-cookies');
const prettyMilliseconds = require('pretty-ms');

async function getCreds()
{
    // "Safe" input from https://stackoverflow.com/a/33500118
    const mutableStdout = new Writable({
        write: function(chunk, encoding, callback)
        {
            if (!this.muted)
                process.stdout.write(chunk, encoding);
            callback();
        }
    });
    mutableStdout.muted = false;
    const rl = readline.createInterface({
        input: process.stdin,
        output: mutableStdout,
        terminal: true
    });
    
    return new Promise(resolve =>
    {
        rl.question('Riot username: ', username =>
        {
            rl.question('Riot password: ', password =>
            {
                rl.close();
                console.log('');
                resolve({username, password});
            });
            mutableStdout.muted = true;
        });
    })
}

function createLogger()
{
    const {combine, timestamp, label, printf} = winston.format;
    const formatPrint = printf(({ level, message, label, timestamp }) => {
        return `${timestamp} [${level}]: ${message}`;
    });
    const format = combine(
        label({ label: '' }),
        timestamp(),
        formatPrint
    );
    return winston.createLogger({
        level: 'info',
        format,
        defaultMeta: {service: 'user-service'},
        transports: [
            new winston.transports.File({filename: path.join(__dirname, 'logs', 'error.log'), level: 'error'}),
            new winston.transports.File({filename: path.join(__dirname, 'logs', 'combined.log')}),
            new winston.transports.Console({level: 'info', format})
        ],
    });
}

function getTokenDataFromURL(url)
{
    try
    {
        const searchParams = new URLSearchParams((new URL(url)).hash.slice(1));
        return {
            accessToken: searchParams.get('access_token'),
            expiresIn: searchParams.get('expires_in')
        };
    }
    catch(err)
    {
        throw new Error(`Bad url: "${url}"`);
    }
}

async function login({username, password}, jar)
{
    const headers = {
        'Content-Type': 'application/json',
        'User-Agent': ''
    };
    
    // Set up cookies for auth request
    await (await fetch(jar, 'https://auth.riotgames.com/api/v1/authorization', {
        method: 'POST',
        body: '{"client_id":"play-valorant-web-prod","nonce":"1","redirect_uri":"https://playvalorant.com/opt_in","response_type":"token id_token"}',
        headers
    })).text();
    
    // Perform auth request
    const authResponse = await (await fetch(jar, 'https://auth.riotgames.com/api/v1/authorization', {
        method: 'PUT',
        body: JSON.stringify({
            type: 'auth',
            username,
            password,
            remember: true,
            language: 'en_US'
        }),
        headers
    })).json();
    
    if(authResponse['error'])
    {
        if(authResponse['error'] === 'auth_failure')
        {
            throw new Error('Invalid Riot username or password');
        }
        else
        {
            throw new Error(`Unknown error: ${authResponse}`);
        }
    }
    
    return getTokenDataFromURL(authResponse['response']['parameters']['uri']);
}

async function reauthToken(jar)
{
    const response = await fetch(jar, 'https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token', {
        headers: {
            'User-Agent': ''
        },
        follow: 0,
        redirect: 'manual'
    });
    const redirectUri = response.headers.get('location');
    return getTokenDataFromURL(redirectUri);
}

async function createCookiesDir()
{
    try
    {
        await fs.promises.mkdir(path.join(__dirname, 'cookies'));
    }
    catch(ignored) {}
}

async function jarLogin(logger, jar, creds)
{
    const loginData = await login(creds, jar);
    await jar.save();
    logger.info(`Got token: ${loginData.accessToken}`);
    logger.info(`Expires in ${loginData.expiresIn} seconds`);
    return loginData;
}

function getSSIDCookie(jar)
{
    const domainCookies = jar.cookiesDomain('auth.riotgames.com');
    for(const cookie of domainCookies)
    {
        if(cookie.name === 'ssid')
        {
            return cookie;
        }
    }
    return null;
}

(async () =>
{
    const logger = createLogger();
    
    await createCookiesDir();
    const jar = new CookieJar(path.join(__dirname, 'cookies', 'jar.json'));
    const longjar = new CookieJar(path.join(__dirname, 'cookies', 'long-jar.json'));
    
    if(process.argv.length > 2 && process.argv[2] === '--resume')
    {
        logger.info('Resuming...');
        await jar.load();
        await longjar.load();
    }
    else
    {
        logger.info('Getting credentials');
        const creds = await getCreds();
        logger.info(`Username: ${creds.username}`);
        
        try
        {
            logger.info('Logging in for repeated tests...');
            await jarLogin(logger, jar, creds);
            logger.info('Logging in for long-term test...');
            await jarLogin(logger, longjar, creds);
        }
        catch(e)
        {
            logger.error('Login failed');
            logger.error(e.toString());
            return;
        }
    }
    
    const printCookieExpireInfo = () =>
    {
        [{name: 'repeated', jar}, {name: 'long-term', jar: longjar}].map(({name, jar}) =>
        {
            return {name, cookie: getSSIDCookie(jar)};
        }).forEach(({name, cookie}) =>
        {
            if(cookie === null || cookie.hasExpired(true))
            {
                logger.info(`${name} ssid cookie expired!`);
            }
            else
            {
                const expiresIn = cookie.expiry.getTime() - (new Date()).getTime();
                logger.info(`${name} ssid cookie expires in ${prettyMilliseconds(expiresIn)} (at ${cookie.expiry.getTime()})`);
            }
        });
    };
    
    const checkCookiesAndGenerateToken = async () =>
    {
        try
        {
            logger.info('   ---   Checking Cookies   ---   ');
            printCookieExpireInfo();
            logger.info('Generating token for repeated tests...');
            const reauthData = await reauthToken(jar);
            logger.info(JSON.stringify(reauthData));
    
            const longCookie = getSSIDCookie(longjar);
            if(longCookie.hasExpired(true))
            {
                logger.info('Long-term cookie has expired! Modifying expiration...');
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                longCookie.expiry = tomorrow;
                logger.info('New expiration:');
                printCookieExpireInfo();
                logger.info('Trying to generate token...');
                const longReauthData = await reauthToken(longjar);
                logger.info(JSON.stringify(longReauthData));
            }
            
            logger.info('Current expirations:');
            printCookieExpireInfo();
            logger.info('Saving cookies...');
            await Promise.all([jar.save(), longjar.save()]);
    
            logger.info('   ---   Finished Checking Cookies   ---   ');
        }
        catch(e)
        {
            logger.error('Error while checking cookies and generating tokens:');
            logger.error(e.toString());
        }
    };
    
    // Run checks on startup
    await checkCookiesAndGenerateToken();
    
    // Run checks every 45 minutes
    setInterval(checkCookiesAndGenerateToken, 45 * 60 * 1000);
})();
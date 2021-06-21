<!-- 
################# CODE FROM BURAKDEV ##############################
#
# https://gist.github.com/BurakDev/fa802dfb9866f34b90fa7502ef11291b
#
###################################################################
-->

<?php
function login($username, $password) {
  $cookies = @tempnam('/tmp', md5($username.$password).'.txt');

  $data = array(
    'client_id' => 'play-valorant-web-prod',
    'nonce' => '1',
    'redirect_uri' => 'https://playvalorant.com/opt_in',
    'response_type' => 'token id_token'
  );

  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, 'https://auth.riotgames.com/api/v1/authorization');
  curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
  curl_setopt($ch, CURLOPT_POST, 1);
  curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_COOKIEJAR, $cookies); 
  curl_setopt($ch, CURLOPT_COOKIEFILE, $cookies);
  $response  = curl_exec($ch);
  curl_close($ch);

  $data = array(
    'type' => 'auth',
    'username' => $username,
    'password' => $password
  );

  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, 'https://auth.riotgames.com/api/v1/authorization');
  curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
  curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PUT');
  curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_COOKIEJAR, $cookies); 
  curl_setopt($ch, CURLOPT_COOKIEFILE, $cookies);
  $response  = curl_exec($ch);
  curl_close($ch);

  $matches = array();

  preg_match('/access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)/', json_decode($response)->response->parameters->uri, $matches);

  $accessToken = $matches[1];
  $idToken = $matches[2];

  $headers = array(
    'Authorization: Bearer '.$accessToken,
    'Content-Type: application/json'
  );

  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, 'https://entitlements.auth.riotgames.com/api/token/v1');
  curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
  curl_setopt($ch, CURLOPT_POST, 1);
  curl_setopt($ch, CURLOPT_POSTFIELDS, '{}');
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_COOKIEJAR, $cookies); 
  curl_setopt($ch, CURLOPT_COOKIEFILE, $cookies);
  $response  = curl_exec($ch);
  curl_close($ch);

  $entitlementsToken = json_decode($response)->entitlements_token;

  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, 'https://auth.riotgames.com/userinfo');
  curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
  curl_setopt($ch, CURLOPT_POST, 1);
  curl_setopt($ch, CURLOPT_POSTFIELDS, '{}');
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_COOKIEJAR, $cookies); 
  curl_setopt($ch, CURLOPT_COOKIEFILE, $cookies);
  $response  = curl_exec($ch);
  curl_close($ch);

  $userId = json_decode($response)->sub;

  return array(
    'accessToken' => $accessToken,
    'idToken' => $idToken,
    'entitlementsToken' => $entitlementsToken,
    'userId' => $userId
  );
}
import time
import json
import oauth2 as oauth
import cnfg

"""
Run this script one time to get
`resource_owner_key` and `resource_owner_secret` to use
Kiva API
"""

config_kiva = cnfg.load(".metis_config")['kiva_api']

# Get consumer_key and consumer_secret from Kiva Developers Site
consumer_key = config_kiva['consumer_key']
consumer_secret = config_kiva['consumer_secret']

# If you have set up a callback URL at build.kiva.org, you should enter it
# below. Otherwise leave it as 'oob'
callback_url = 'oob'

# This is the URL of the protected resource you want to access
resource_url = 'https://api.kivaws.org/v1/my/account.json'

# These should stay the same, probably
request_token_url = 'https://api.kivaws.org/oauth/request_token.json?oauth_callback=oob'
authorize_url = 'https://www.kiva.org/oauth/authorize?response_type=code&oauth_callback=oob' + \
    '&client_id=' + consumer_key + '&scope=access'
access_token_url = 'https://api.kivaws.org/oauth/access_token'

# Leave everything below this line alone
consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)

# Step 1: Get a request token. This is a temporary token that is used for
# having the user authorize an access token and to sign the request to obtain
# said access token.

resp, content = client.request(request_token_url, "POST")

if resp['status'] != '200':
    raise Exception("Invalid response. Status: " +
                    resp['status'] + " Message: " + content)

content = content.decode('utf-8')
request_token = dict(json.loads(str(content)))

print ('Request Token: ', str(content))

# Step 2: Redirect to the provider. Since this is a CLI script we do not
# redirect. In a web application you would redirect the user to the URL
# below.

print ("%s&oauth_token=%s" % (authorize_url, request_token['oauth_token']))

# After the user has granted access to you, the consumer, the provider will
# redirect you to whatever URL you have told them to redirect to. You can
# usually define this in the oauth_callback argument as well.
oauth_verifier = input('Enter the code here: ')

# Step 3: Once the consumer has redirected the user back to the oauth_callback
# URL you can request the access token the user has approved. You use the
# request token to sign this request. After this is done you throw away the
# request token and use the access token returned. You should store this
# access token somewhere safe, like a database, for future use.

token = oauth.Token(request_token['oauth_token'], request_token[
    'oauth_token_secret'])
token.set_verifier(oauth_verifier)
client = oauth.Client(consumer, token)

resp, content = client.request(access_token_url, "POST")
content = content.decode('utf-8')

print('Access Token Url: ', access_token_url)
print ('ACCESS TOKEN: ', str(content))

if resp['status'] != '200':
    raise Exception("Invalid response. Status: " +
                    resp['status'] + " Message: " + content)


access_oauth_token = input('Enter the access oauth token here: ')  # in token
access_oauth_token_secret = input('Enter the access oauth token secret here: ')


# Set the base oauth_* parameters along with any other parameters required
# for the API call.
params = {
    'oauth_version': "1.0",
    'oauth_nonce': oauth.generate_nonce(),
    'oauth_timestamp': int(time.time())
}

# Set our token/key parameters
token = oauth.Token(access_oauth_token,
                    access_oauth_token_secret)
params['oauth_token'] = access_oauth_token
params['oauth_consumer_key'] = consumer.key

# Create our request. Change method, etc. accordingly.
req = oauth.Request(method="GET", url=resource_url, parameters=params)

# Sign the request.
signature_method = oauth.SignatureMethod_HMAC_SHA1()
req.sign_request(signature_method, consumer, token)
client = oauth.Client(consumer, token)
resp, content = client.request(resource_url, "GET")

content = content.decode('utf-8')
print(content)
if resp['status'] != '200':
    raise Exception("Invalid response. Status: " +
                    resp['status'] + " Message: " + content)

print (content)

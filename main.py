
# Define imports
import msal

# Enter the details of your AAD app registration
client_id = '8da7ecf6-6daf-4b94-98a1-a369051e1f3f'
client_secret = 'QUb8Q~IwE59T_yyXOi10vq6xumpbZtChemfnpaXI'
authority = 'https://login.microsoftonline.com/4e51e906-7ac3-4230-8c71-e74551315932'
scope = ['https://graph.microsoft.com/.default']

# Create an MSAL instance providing the client_id, authority and client_credential parameters
client = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

# First, try to lookup an access token in cache
token_result = client.acquire_token_silent(scope, account=None)

# If the token is available in cache, save it to a variable
if token_result:
  access_token = 'Bearer ' + token_result['access_token']
  print('Access token was loaded from cache')

# If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
if not token_result:
  token_result = client.acquire_token_for_client(scopes=scope)
  access_token = 'Bearer ' + token_result['access_token']
  print('New access token was acquired from Azure AD')

print(access_token)




# Define imports
import requests

# Copy access_token and specify the MS Graph API endpoint you want to call, e.g. 'https://graph.microsoft.com/v1.0/groups' to get all groups in your organization
url = 'https://graph.microsoft.com/v1.0/groups'
headers = {
  'Authorization': access_token
}

# Make a GET request to the provided url, passing the access token in a header
graph_result = requests.get(url=url, headers=headers)

# Print the results in a JSON format
print(graph_result.json())
from configparser import SectionProxy
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import (
    MessagesRequestBuilder)
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody)
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress

#from msgraph.generated.models.get_member_groups_post_request_body import GetMemberGroupsPostRequestBody

class Graph:
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        #tenant_id = self.settings['tenantId']
        #graph_scopes = self.settings['graphUserScopes'].split(' ')

        #self.device_code_credential = DeviceCodeCredential(client_id, tenant_id = tenant_id)
        #self.user_client = GraphServiceClient(self.device_code_credential, graph_scopes)


    async def get_user_token(self):
        #graph_scopes = self.settings['graphUserScopes']
        #access_token = self.device_code_credential.get_token(graph_scopes)

        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']

        import msal
        # Enter the details of your AAD app registration
        client_secret = 'QUb8Q~IwE59T_yyXOi10vq6xumpbZtChemfnpaXI'
        authority = 'https://login.microsoftonline.com/' + tenant_id
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



        return access_token.token
    
    async def get_user(self):
        # Only request specific properties using $select
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName','id']
        )

        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        user = await self.user_client.me.get(request_configuration=request_config)

        return user
    
    async def get_user_groups(self):
        result = self.user_client.groups.get()
        return result
        #request_body = GetMemberGroupsPostRequestBody(security_enabled_only = True)
        #result = self.user_client.me.get_member_groups.post(request_body)    
    
    async def make_graph_call(self):
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName','id']
        )
        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        user = await self.user_client.me.get(request_configuration=request_config)
        result = await self.user_client.users.by_user_id(user.id).member_of.get()

        #users = await self.user_client.users.get()
        #if users and users.value:
        #    for user in users.value:
        #        print("User: ", user.id, user.display_name, user.mail)


        #request_body = GetMemberGroupsPostRequestBody(
        #    security_enabled_only = True,
        #)
        #result = await self.user_client.me.get_member_groups.post(request_body)
         

        # Only request specific properties using $select
        #query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
        #    select=['displayName', 'mail', 'userPrincipalName','id']
        #)
        
        # Only request specific properties using $select
        #query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
        #    select=['displayName', 'mail', 'userPrincipalName']
        #)
        #request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
        #    query_parameters=query_params
        #)
        #user = await self.user_client.me.get(request_configuration=request_config)
        return result
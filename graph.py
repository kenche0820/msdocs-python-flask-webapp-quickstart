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

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.permissions.kind import PermissionKind



class Graph:
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id = tenant_id)
        self.user_client = GraphServiceClient(self.device_code_credential, graph_scopes)

    #    from tests import (
    #        test_team_site_url,
    #        test_user_credentials,
    #        test_user_principal_name_alt,
    #    )
        test_team_site_url = ""
        test_user_credentials = ""
        test_user_principal_name_alt = ""

        client = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
        file_url = result["metadata_spo_item_name"]

        target_user = client.web.site_users.get_by_email(test_user_principal_name_alt)
        target_file = client.web.get_file_by_server_relative_path(file_url)
        myPermission = target_file.listItemAllFields.get_user_effective_permissions(
            target_user
        ).execute_query()
        # verify whether user has Reader role to a file
        if myPermission.value.has(PermissionKind.OpenItems):
            print("User has access to read a file")











    async def get_user_token(self):
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
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
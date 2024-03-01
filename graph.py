from configparser import SectionProxy
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.users_request_builder import UsersRequestBuilder

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.permissions.kind import PermissionKind


class Graph:
    settings: SectionProxy
    client_credential: ClientSecretCredential
    app_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        client_secret = self.settings['clientSecret']

        self.client_credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        self.app_client = GraphServiceClient(self.client_credential) # type: ignore

    async def get_app_only_token(self):
        graph_scope = 'https://graph.microsoft.com/.default'
        access_token = await self.client_credential.get_token(graph_scope)
        return access_token.token
    
    async def get_users(self):
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            # Only request specific properties
            select = ['displayName', 'id', 'mail'],
            # Get at most 25 results
            top = 25,
            # Sort by display name
            orderby= ['displayName']
        )
        request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        users = await self.app_client.users.get(request_configuration=request_config)
        return users    
    
    async def make_graph_call(self):
        scopes = ['https://graph.microsoft.com/.default']
        graph_client = GraphServiceClient(self.client_credential, scopes)

        user = await graph_client.users.by_user_id('561ca5be-74b7-4d96-a878-5185a54eff2e').member_of.get()


        
        test_team_site_url = "https://setelab.sharepoint.com/"
    
        client_id = self.settings['clientId']
        client_secret = self.settings['clientSecret']



        ctx = ClientContext(test_team_site_url).with_client_credentials(
            client_id, client_secret
        )



        file_url = "Shared Documents/Group_Benefits.pdf"

        target_user = user
        target_file = ctx.web.get_file_by_server_relative_path(file_url)
        result = target_file.listItemAllFields.get_user_effective_permissions(
            target_user
        ).execute_query()
        # verify whether user has Reader role to a file
        if result.value.has(PermissionKind.OpenItems):
            print("User has access to read a file")        

        return result
import asyncio
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder
from langchain.schema import Document
import os

class OutlookAdaptor:
    """
    An adaptor to connect to Microsoft Outlook and fetch emails for a specific user
    using the Microsoft Graph API with application permissions (Client Credentials Flow).
    Suitable for headless/daemon applications.
    """

    def __init__(self, client_id: str, client_secret: str, tenant_id: str, user_principal_name: str):
        if not all([client_id, client_secret, tenant_id, user_principal_name]):
            raise ValueError("Client ID, Client Secret, Tenant ID, and User Principal Name are required.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.user_principal_name = user_principal_name
        self.scopes = ['https://graph.microsoft.com/.default']
        self.graph_client = self._create_graph_client()

    def _create_graph_client(self):
        """Creates a GraphServiceClient with a client secret credential."""
        credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        graph_client = GraphServiceClient(credentials=credential, scopes=self.scopes)
        return graph_client

    async def _fetch_emails(self, top: int = 10):
        """
        Asynchronously fetches emails from the specified user's inbox.
        """
        try:
            # Define the query parameters using the request builder
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                select=["subject", "body", "sender", "receivedDateTime"],
                top=top,
                orderby=["receivedDateTime DESC"]
            )

            request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )

            # Fetch messages for a specific user
            messages = await self.graph_client.users.by_user_id(self.user_principal_name).messages.get(
                request_configuration=request_config
            )
            return messages.value if messages else []
        except Exception as e:
            print(f"An error occurred while fetching emails: {e}")
            return []

    def load_documents(self, max_emails: int = 10) -> list[Document]:
        """
        Loads emails from Outlook and converts them into LangChain Document objects.

        :param max_emails: The maximum number of emails to fetch.
        :return: A list of Document objects.
        """
        print(f"Fetching last {max_emails} emails from Outlook for user: {self.user_principal_name}...")

        try:
            messages = asyncio.run(self._fetch_emails(top=max_emails))
        except Exception as e:
            print(f"Error running async email fetch: {e}")
            messages = []

        if not messages:
            print("No emails found or failed to fetch.")
            return []

        documents = []
        for msg in messages:
            content = msg.body.content if msg.body and msg.body.content else ""
            metadata = {
                "source": "outlook",
                "subject": msg.subject or "N/A",
                "sender": msg.sender.email_address.address if msg.sender and msg.sender.email_address else "N/A",
                "received_datetime": msg.received_date_time.isoformat() if msg.received_date_time else "N/A",
            }
            documents.append(Document(page_content=content, metadata=metadata))

        print(f"Successfully loaded {len(documents)} emails from Outlook.")
        return documents

if __name__ == '__main__':
    # This is an example of how to use the OutlookAdaptor in a headless environment.
    # You would need to set your credentials in your environment or a config file.

    CLIENT_ID = os.environ.get("OUTLOOK_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("OUTLOOK_CLIENT_SECRET")
    TENANT_ID = os.environ.get("OUTLOOK_TENANT_ID")
    USER_PRINCIPAL_NAME = os.environ.get("OUTLOOK_USER_PRINCIPAL_NAME")

    if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID, USER_PRINCIPAL_NAME]):
        print("Please set the following environment variables:")
        print(" - OUTLOOK_CLIENT_ID")
        print(" - OUTLOOK_CLIENT_SECRET")
        print(" - OUTLOOK_TENANT_ID")
        print(" - OUTLOOK_USER_PRINCIPAL_NAME")
    else:
        adaptor = OutlookAdaptor(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            tenant_id=TENANT_ID,
            user_principal_name=USER_PRINCIPAL_NAME
        )
        docs = adaptor.load_documents(max_emails=5)

        if docs:
            print("\n--- Fetched Documents ---")
            for doc in docs:
                print(f"Subject: {doc.metadata['subject']}")
                print(f"From: {doc.metadata['sender']}")
                print(f"Date: {doc.metadata['received_datetime']}")
                print(f"Body Preview: {doc.page_content[:100]}...")
                print("-" * 20)

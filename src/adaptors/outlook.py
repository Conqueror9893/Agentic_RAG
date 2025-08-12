import asyncio
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from langchain.schema import Document

class OutlookAdaptor:
    """
    An adaptor to connect to Microsoft Outlook and fetch emails using the Microsoft Graph API.
    """

    def __init__(self, client_id: str, tenant_id: str):
        if not client_id or not tenant_id:
            raise ValueError("Client ID and Tenant ID are required for OutlookAdaptor.")

        self.client_id = client_id
        self.tenant_id = tenant_id
        self.scopes = ['https://graph.microsoft.com/.default']
        self.graph_client = self._create_graph_client()

    def _create_graph_client(self):
        """Creates a GraphServiceClient with a device code credential."""
        credential = DeviceCodeCredential(client_id=self.client_id, tenant_id=self.tenant_id)
        graph_client = GraphServiceClient(credentials=credential, scopes=self.scopes)
        return graph_client

    async def _fetch_emails(self, top: int = 10):
        """
        Asynchronously fetches emails from the user's inbox.
        """
        try:
            messages = await self.graph_client.me.messages.get(
                query_params={
                    "select": ["subject", "body", "sender", "receivedDateTime"],
                    "top": top,
                    "orderby": "receivedDateTime DESC"
                }
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
        print("Fetching emails from Outlook...")
        print("Please follow the instructions to authenticate with your Microsoft account.")

        try:
            # Run the async fetch_emails method
            messages = asyncio.run(self._fetch_emails(top=max_emails))
        except Exception as e:
            # Catch exceptions from asyncio.run if it's called in an environment with a running loop
            print(f"Error running async email fetch: {e}")
            messages = []

        if not messages:
            print("No emails found or failed to fetch.")
            return []

        documents = []
        for msg in messages:
            content = msg.body.content if msg.body else ""
            metadata = {
                "source": "outlook",
                "subject": msg.subject,
                "sender": msg.sender.email_address.address if msg.sender and msg.sender.email_address else "N/A",
                "received_datetime": msg.received_date_time.isoformat() if msg.received_date_time else "N/A",
            }
            documents.append(Document(page_content=content, metadata=metadata))

        print(f"Successfully loaded {len(documents)} emails from Outlook.")
        return documents

if __name__ == '__main__':
    # This is an example of how to use the OutlookAdaptor
    # You would need to set your CLIENT_ID and TENANT_ID in your environment or a config file
    import os

    CLIENT_ID = os.environ.get("OUTLOOK_CLIENT_ID")
    TENANT_ID = os.environ.get("OUTLOOK_TENANT_ID")

    if not CLIENT_ID or not TENANT_ID:
        print("Please set the OUTLOOK_CLIENT_ID and OUTLOOK_TENANT_ID environment variables.")
    else:
        adaptor = OutlookAdaptor(client_id=CLIENT_ID, tenant_id=TENANT_ID)
        docs = adaptor.load_documents(max_emails=5)

        if docs:
            print("\n--- Fetched Documents ---")
            for doc in docs:
                print(f"Subject: {doc.metadata['subject']}")
                print(f"From: {doc.metadata['sender']}")
                print(f"Date: {doc.metadata['received_datetime']}")
                print(f"Body Preview: {doc.page_content[:100]}...")
                print("-" * 20)

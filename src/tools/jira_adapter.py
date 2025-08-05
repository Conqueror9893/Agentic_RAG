import os
from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.tools.jira_loader import JiraLoader

class JiraAdapter:
    """
    An adapter to connect Jira as a data source for the agentic RAG system.
    This class uses the JiraLoader to fetch data from Jira and transforms it
    into a format that can be used by the vector store.
    """
    def __init__(self, jira_loader: JiraLoader):
        """
        Initializes the JiraAdapter with a JiraLoader instance.
        """
        self.jira_loader = jira_loader

    def load_and_split(self, project_key: str, user_email: str) -> list[Document]:
        """
        Fetches all relevant data from Jira for a given project and user,
        and splits it into chunks.
        """
        print(f"Fetching Jira data for project '{project_key}' and user '{user_email}'...")

        # Fetch all tickets for the user
        user_tickets_str = self.jira_loader.get_user_tickets(user_email)

        # In a real-world scenario, you might want to fetch other data as well,
        # such as project status, worklogs, comments, etc.
        # For now, we'll just use the user's tickets as the data source.

        if not user_tickets_str or "No tickets found" in user_tickets_str:
            print("No documents to load from Jira.")
            return []

        # Convert the string data into a LangChain Document
        # We use a single document for all the tickets, but you could also
        # create one document per ticket.
        documents = [Document(page_content=user_tickets_str, metadata={"source": "jira"})]

        # Split the document into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunked_documents = text_splitter.split_documents(documents)

        print(f"Loaded and split Jira data into {len(chunked_documents)} chunks.")

        return chunked_documents

if __name__ == '__main__':
    # This is for testing the Jira adapter in isolation.
    # Note: To run this, you need to have a .env file with your JIRA credentials.
    from config import JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN

    if all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
        try:
            jira_loader = JiraLoader()
            jira_adapter = JiraAdapter(jira_loader)

            # Replace with a real project key and user email for testing
            project_key = "PROJ"  # e.g., "MYPROJ"
            user_email = "test@example.com"  # e.g., "user@yourdomain.com"

            docs = jira_adapter.load_and_split(project_key, user_email)
            if docs:
                print(f"Successfully loaded {len(docs)} chunks from Jira.")
                print("First chunk:")
                print(docs[0].page_content)
                print("\nMetadata:")
                print(docs[0].metadata)
            else:
                print("No data was loaded from Jira.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("Jira credentials not found in .env file. Skipping JiraAdapter test.")

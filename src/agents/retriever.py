from src.tools.jira_adapter import JiraAdapter
from src.tools.vector_store import add_documents_to_store
import re

class Retriever:
    """
    This agent retrieves relevant documents from the vector store.
    It can be configured to load data from Jira if a JiraAdapter is provided.
    """
    def __init__(self, vector_store, jira_adapter: JiraAdapter = None):
        self.vector_store = vector_store
        self.jira_adapter = jira_adapter

    def retrieve(self, queries: list[str], k: int = 2) -> list[str]:
        """
        Retrieves documents for the given queries from the vector store.
        If a query contains "JIRA", it will first load the data from Jira,
        add it to the vector store, and then perform the search.
        """
        print(f"Retrieving documents for queries: {queries}")

        # Check if any query is a Jira query
        is_jira_query = any("jira" in q.lower() for q in queries)

        if self.jira_adapter and is_jira_query:
            print("Jira query detected. Loading data from Jira...")
            # In a real application, you would parse the project key and user from the query.
            # For this example, we'll use placeholder values.
            # You might need to implement a more sophisticated mechanism to extract these.
            project_key = "PROJ"  # Placeholder
            user_email = "test@example.com"  # Placeholder

            # Load documents from Jira
            jira_docs = self.jira_adapter.load_and_split(project_key, user_email)

            if jira_docs:
                # Add the new documents to the vector store
                add_documents_to_store(self.vector_store, jira_docs)
                print(f"Added {len(jira_docs)} new documents from Jira to the vector store.")
            else:
                print("No documents were loaded from Jira.")

        # Retrieve documents from the vector store for all queries
        retrieved_docs = []
        for query in queries:
            docs = self.vector_store.similarity_search(query, k=k)
            retrieved_docs.extend([doc.page_content for doc in docs])

        # Get unique documents by their content
        unique_docs_by_content = set(retrieved_docs)

        print(f"Retrieved {len(unique_docs_by_content)} unique documents.")

        return list(unique_docs_by_content)

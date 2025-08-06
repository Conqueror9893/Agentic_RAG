# # from src.tools.jira_adapter import JiraAdapter
# # from src.tools.vector_store import add_documents_to_store
# # import re

# # class Retriever:
# #     """
# #     This agent retrieves relevant documents from the vector store.
# #     It can be configured to load data from Jira if a JiraAdapter is provided.
# #     """
# #     def __init__(self, vector_store, jira_adapter: JiraAdapter = None):
# #         self.vector_store = vector_store
# #         self.jira_adapter = jira_adapter

# #     def retrieve(self, queries: list[str], k: int = 2) -> list[str]:
# #         """
# #         Retrieves documents for the given queries from the vector store.
# #         If a query contains "JIRA", it will first load the data from Jira,
# #         add it to the vector store, and then perform the search.
# #         """
# #         print(f"Retrieving documents for queries: {queries}")

# #         # Check if any query is a Jira query
# #         is_jira_query = any("jira" in q.lower() for q in queries)

# #         if self.jira_adapter and is_jira_query:
# #             print("Jira query detected. Loading data from Jira...")
# #             # In a real application, you would parse the project key and user from the query.
# #             # For this example, we'll use placeholder values.
# #             # You might need to implement a more sophisticated mechanism to extract these.
# #             project_key = "PROJ"  # Placeholder
# #             user_email = "test@example.com"  # Placeholder

# #             # Load documents from Jira
# #             jira_docs = self.jira_adapter.load_and_split(project_key, user_email)

# #             if jira_docs:
# #                 # Add the new documents to the vector store
# #                 add_documents_to_store(self.vector_store, jira_docs)
# #                 print(f"Added {len(jira_docs)} new documents from Jira to the vector store.")
# #             else:
# #                 print("No documents were loaded from Jira.")

# #         # Retrieve documents from the vector store for all queries
# #         retrieved_docs = []
# #         for query in queries:
# #             docs = self.vector_store.similarity_search(query, k=k)
# #             retrieved_docs.extend([doc.page_content for doc in docs])

# #         # Get unique documents by their content
# #         unique_docs_by_content = set(retrieved_docs)

# #         print(f"Retrieved {len(unique_docs_by_content)} unique documents.")

# #         return list(unique_docs_by_content)


# # from src.tools.jira_adapter import JiraAdapter
# # from src.tools.vector_store import add_documents_to_store
# # from src.tools.llm_interface import run_ollama_model  # Optional for intent parsing
# # import os

# # class Retriever:
# #     """
# #     This agent retrieves relevant documents from the vector store.
# #     It can be configured to load data from Jira if a JiraAdapter is provided.
# #     """
# #     def __init__(self, vector_store, jira_adapter: JiraAdapter = None):
# #         self.vector_store = vector_store
# #         self.jira_adapter = jira_adapter

# #     def retrieve(self, queries: list[str], k: int = 2) -> list[str]:
# #         """
# #         Retrieves documents for the given queries from the vector store.
# #         If a query contains "JIRA", it will first load the data from Jira,
# #         add it to the vector store, and then perform the search.
# #         """
# #         print(f"Retrieving documents for queries: {queries}")

# #         # Check if any query is a Jira query
# #         is_jira_query = any("jira" in q.lower() for q in queries)

# #         if self.jira_adapter and is_jira_query:
# #             print("Jira query detected. Loading data from Jira...")

# #             # Use your actual Jira credentials
# #             user_email = "syed.tajamul@i-exceed.com"
# #             project_key = "PSA"
# #             ticket_id = "PSA-462"

# #             # Load documents from Jira (your adapter must support this)
# #             jira_docs = self.jira_adapter.load_ticket(ticket_id, user_email)

# #             if jira_docs:
# #                 add_documents_to_store(self.vector_store, jira_docs)
# #                 print(f"Added {len(jira_docs)} new documents from Jira ticket {ticket_id}.")
# #             else:
# #                 print("No documents were loaded from Jira.")

# #         # Retrieve documents from the vector store for all queries
# #         retrieved_docs = []
# #         for query in queries:
# #             docs = self.vector_store.similarity_search(query, k=k)
# #             retrieved_docs.extend([doc.page_content for doc in docs])

# #         # Unique by content
# #         unique_docs_by_content = set(retrieved_docs)
# #         print(f"Retrieved {len(unique_docs_by_content)} unique documents.")

# #         return list(unique_docs_by_content)


# from src.tools.jira_adapter import JiraAdapter
# from src.tools.vector_store import add_documents_to_store
# from src.tools.llm_interface import run_ollama_model  # Optional for intent parsing
# import os

# class Retriever:
#     """
#     This agent retrieves relevant documents from the vector store.
#     It can optionally enrich the store with tickets from Jira using JiraAdapter.
#     """

#     def __init__(self, vector_store, jira_adapter: JiraAdapter = None):
#         self.vector_store = vector_store
#         self.jira_adapter = jira_adapter

#     def retrieve(self, queries: list[str], k: int = 2) -> list[str]:
#         """
#         Retrieves documents for the given queries from the vector store.
#         If a query mentions 'jira', it loads and indexes data from Jira.
#         """
#         print(f"Retrieving documents for queries: {queries}")

#         is_jira_query = any("jira" in q.lower() for q in queries)

#         if self.jira_adapter and is_jira_query:
#             print("Jira query detected. Loading data from Jira...")

#             user_email = "syed.tajamul@i-exceed.com"
#             project_key = "PSA"

#             # Step 1: Load all tickets in the project
#             tickets = self.jira_adapter.fetch_all_issues_with_details(project_key)

#             if tickets:
#                 print(f"Fetched {len(tickets)} tickets from Jira.")

#                 # Optional: Flatten sub-tasks into main ticket list
#                 all_docs = []
#                 for ticket in tickets:
#                     all_docs.append(ticket)

#                     # Fetch and add subtasks if available
#                     if "subtasks" in ticket.metadata:
#                         all_docs.extend(ticket.metadata["subtasks"])

#                 # Step 2: Add all to vector store
#                 add_documents_to_store(self.vector_store, all_docs)
#                 print(f"Indexed {len(all_docs)} Jira documents into the vector store.")
#             else:
#                 print("No tickets found in Jira.")

#         # Step 3: Search using the vector store
#         retrieved_docs = []
#         for query in queries:
#             docs = self.vector_store.similarity_search(query, k=k)
#             retrieved_docs.extend([doc.page_content for doc in docs])

#         # Return unique document content
#         unique_docs = list(set(retrieved_docs))
#         print(f"Retrieved {len(unique_docs)} unique documents.")
#         return unique_docs


from src.tools.jira_adapter import JiraAdapter
from src.tools.vector_store import add_documents_to_store
from langchain.schema import Document

class Retriever:
    """
    This agent retrieves relevant documents from the vector store.
    It can enrich the store with Jira issues via JiraAdapter.
    """
    def __init__(self, vector_store, jira_adapter: JiraAdapter = None):
        self.vector_store = vector_store
        self.jira_adapter = jira_adapter
        self._initialized = False
        if self.jira_adapter:
            self._populate_jira_documents()
            
    def _populate_jira_documents(self):
        if self._initialized:
            return
        print("Fetching Jira issues and populating vector store...")
        raw_issues = self.jira_adapter.fetch_all_issues_with_details()
        documents = [Document(
            page_content=self._compose_issue_text(issue),
            metadata={
                "issue_key": issue["key"],
                "assignee": issue["assignee"],
                "reporter": issue["reporter"],
                "status": issue["status"],
                "created": issue["created"],
                "updated": issue["updated"],
                "priority": issue["priority"],
                "issuetype": issue["issuetype"],
                "labels": ", ".join(issue.get("labels", [])),
                
                "subtasks": "; ".join(
                    f"{sub['key']} - {sub['summary']} ({sub['status']})"
                    for sub in issue.get("subtasks", [])
                ),

            }) for issue in raw_issues]

        if documents:
            add_documents_to_store(self.vector_store, documents)
            print(f"Added {len(documents)} Jira documents to vector store.")
        else:
            print("No documents fetched from Jira.")
        self._initialized = True

    def retrieve(self, intent: str, queries: list[str], k: int = 2) -> list[str]:
        print(f"Retrieving documents for intent: {intent} and queries: {queries}")
        
        retrieved_docs = []

        for query in queries:
            # Optional: route based on intent
            if intent.lower() == "jira":
                # Perform JIRA-related similarity search
                results = self.vector_store.similarity_search(query, k=k)
            else:
                # Placeholder for future intent types
                print(f"[WARN] Unknown intent '{intent}', falling back to default vector store.")
                results = self.vector_store.similarity_search(query, k=k)

            retrieved_docs.extend([doc.page_content for doc in results])

        unique_docs = list(set(retrieved_docs))
        print(f"Retrieved {len(unique_docs)} unique documents.")
        return unique_docs

    
    def _compose_issue_text(self, issue: dict) -> str:
        """
        Converts an enriched Jira issue into a text block for embedding.
        """
        lines = [
            f"Issue: {issue['key']}",
            f"Summary: {issue.get('summary', '')}",
            f"Status: {issue.get('status', '')}",
            f"Issue Type: {issue.get('issuetype', '')}",
            f"Priority: {issue.get('priority', '')}",
            f"Assignee: {issue.get('assignee', '')}",
            f"Reporter: {issue.get('reporter', '')}",
            f"Created: {issue.get('created', '')}",
            f"Updated: {issue.get('updated', '')}",
            f"Labels: {', '.join(issue.get('labels', []))}",
            f"\nDescription:\n{issue.get('description', '')}",
        ]

        # Add subtasks
        if issue.get("subtasks"):
            lines.append("\nSubtasks:")
            for sub in issue["subtasks"]:
                lines.append(
                    f"- {sub['key']}: {sub['summary']} (Status: {sub['status']})"
                )

        return "\n".join(lines)

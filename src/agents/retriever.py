from src.tools.jira_loader import JiraLoader
import re

class Retriever:
    """
    This agent retrieves relevant documents from the vector store or Jira
    based on the rephrased queries.
    """
    def __init__(self, vector_store, jira_loader=None):
        self.vector_store = vector_store
        self.jira_loader = jira_loader or JiraLoader()

    def retrieve(self, queries: list[str], k: int = 2) -> list[str]:
        """
        Retrieves documents for the given queries. If a query contains "JIRA",
        it will be routed to the JiraLoader.
        """
        print(f"Retrieving documents for queries: {queries}")

        retrieved_docs = []
        jira_queries = [q for q in queries if "jira" in q.lower()]
        vector_store_queries = [q for q in queries if "jira" not in q.lower()]

        if jira_queries:
            print(f"Jira queries identified: {jira_queries}")
            for query in jira_queries:
                # Basic parsing to extract relevant information from the query
                # This can be improved with a more sophisticated NLP approach
                if "time" in query.lower() and "work on" in query.lower():
                    # Example: "How much time did person X work on project Y in JIRA"
                    match = re.search(r"person (\S+) work on project (\S+)", query, re.IGNORECASE)
                    if match:
                        user, project = match.groups()
                        retrieved_docs.append(self.jira_loader.get_user_worklogs(project, user))
                elif "status on project" in query.lower():
                    # Example: "What is the latest status on Project Y in JIRA"
                    match = re.search(r"status on project (\S+)", query, re.IGNORECASE)
                    if match:
                        project = match.group(1)
                        retrieved_docs.append(self.jira_loader.get_project_status(project))
                elif "tickets are being worked upon by" in query.lower():
                    # Example: "what tickets are being worked upon by Person X in JIRA"
                    match = re.search(r"worked upon by (\S+)", query, re.IGNORECASE)
                    if match:
                        user = match.group(1)
                        retrieved_docs.append(self.jira_loader.get_user_tickets(user))
                else:
                    retrieved_docs.append("Unsupported JIRA query. Please ask about project status, user worklogs, or user tickets.")

        if vector_store_queries:
            print(f"Vector store queries identified: {vector_store_queries}")
            for query in vector_store_queries:
                docs = self.vector_store.similarity_search(query, k=k)
                retrieved_docs.extend([doc.page_content for doc in docs])

        # Get unique documents by their content
        unique_docs_by_content = set(retrieved_docs)

        print(f"Retrieved {len(unique_docs_by_content)} unique documents.")

        return list(unique_docs_by_content)

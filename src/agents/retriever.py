from src.tools.jira_loader import JiraLoader
import re
from src.tools.llm_interface import run_ollama_model

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
                try:
                    parsed = run_ollama_model(query)
                    intent = parsed.get("intent", "unsupported")
                    params = parsed.get("parameters", {})

                    if intent == "get_user_worklogs":
                        retrieved_docs.append(self.jira_loader.get_user_worklogs(params.get("project"), params.get("user")))
                    elif intent == "get_project_status":
                        retrieved_docs.append(self.jira_loader.get_project_status(params.get("project")))
                    elif intent == "get_user_tickets":
                        retrieved_docs.append(self.jira_loader.get_user_tickets(params.get("user")))
                    else:
                        retrieved_docs.append("Unsupported JIRA query. Please ask about project status, user worklogs, or user tickets.")
                except Exception as e:
                    retrieved_docs.append(f"Error parsing query with LLM: {e}")
                if vector_store_queries:
                    print(f"Vector store queries identified: {vector_store_queries}")
                    for query in vector_store_queries:
                        docs = self.vector_store.similarity_search(query, k=k)
                        retrieved_docs.extend([doc.page_content for doc in docs])

        # Get unique documents by their content
        unique_docs_by_content = set(retrieved_docs)

        print(f"Retrieved {len(unique_docs_by_content)} unique documents.")

        return list(unique_docs_by_content)

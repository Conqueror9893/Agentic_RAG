from src.agents.orchestrator import Orchestrator
from src.agents.retriever import Retriever
from src.agents.generator import Generator
from src.agents.rephraser import Rephraser
from src.agents.evaluator import Evaluator
from src.tools.vector_store import get_vector_store
from src.tools.jira_loader import JiraLoader
from src.tools.jira_adapter import JiraAdapter
from config import JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN
import os

def setup_and_run(query: str):
    """
    Sets up the RAG system, configures the Jira adapter, and runs the query.
    """
    print("--- 1. CONFIGURATION AND SETUP ---")
    print("Initializing vector store...")
    vector_store = get_vector_store()

    print("\n--- 2. ADAPTER AND AGENT INITIALIZATION ---")

    # Initialize JiraAdapter if credentials are available
    jira_adapter = None
    if all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
        try:
            jira_loader = JiraLoader()
            jira_adapter = JiraAdapter(jira_loader)
            print("JiraAdapter initialized successfully.")
        except ValueError as e:
            print(f"Could not initialize JiraAdapter: {e}")
            # If Jira is required, you might want to exit here.
            # For this example, we'll continue without the Jira adapter.
    else:
        print("Jira credentials not found in .env file. Jira-related queries will not work.")

    # Initialize agents
    rephraser_agent = Rephraser()
    retriever_agent = Retriever(vector_store=vector_store, jira_adapter=jira_adapter)
    generator_agent = Generator()
    evaluator_agent = Evaluator()

    # Initialize orchestrator
    orchestrator = Orchestrator(
        rephraser=rephraser_agent,
        retriever=retriever_agent,
        generator=generator_agent,
        evaluator=evaluator_agent
    )

    print("\n--- 3. RUNNING THE AGENTIC RAG WORKFLOW ---")
    result_state = orchestrator.run(query)

    print("\n--- 4. WORKFLOW FINISHED ---")
    final_node_state = result_state.get('evaluator', {})
    final_answer = final_node_state.get('final_answer')

    if final_answer:
        print("\nFinal Answer:")
        print(final_answer)
    else:
        print("\nCould not retrieve a final answer.")
        print("Final state:", result_state)

# if __name__ == "__main__":
#     # Example query. Replace with your own.
#     # This query will trigger the JiraAdapter if it's configured.
#     user_query = "what tickets are being worked upon by test@example.com in JIRA"

#     # You can also ask non-Jira questions if you have other data sources,
#     # but this example is focused on the Jira integration.
#     # user_query = "What is LangGraph?"

#     if not user_query:
#         print("Please set a user_query in main.py")
#     else:
#         setup_and_run(user_query)

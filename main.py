from dotenv import load_dotenv
import os

from src.agents.orchestrator import Orchestrator
from src.agents.retriever import Retriever
from src.agents.generator import Generator
from src.agents.rephraser import Rephraser
from src.agents.evaluator import Evaluator
from src.agents.intent_classifier import IntentClassifier
from src.tools.vector_store import get_vector_store
from src.tools.jira_adapter import JiraAdapter
from config import JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN


def setup_and_run(query: str):
    """
    Sets up the RAG system, configures the Jira adapter, and runs the query.
    """
    print("\n\n--- 1. CONFIGURATION AND SETUP ---")
    print("Initializing vector store...")
    vector_store = get_vector_store()

    print("\n--- 2. ADAPTER AND AGENT INITIALIZATION ---")

    # Initialize JiraAdapter if credentials are available
    jira_adapter = None
    if all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
        try:
            # The project key is hardcoded here. In a real application, you might
            # want to make this configurable.
            jira_adapter = JiraAdapter(project_key="PSA")
            print("JiraAdapter initialized successfully.")
        except ValueError as e:
            print(f"Could not initialize JiraAdapter: {e}")
    else:
        print("Jira credentials not found in .env file. Jira-related queries will be skipped.")

    # Initialize agents
    rephraser_agent = Rephraser()
    retriever_agent = Retriever(vector_store=vector_store, jira_adapter=jira_adapter)
    generator_agent = Generator()
    evaluator_agent = Evaluator()
    intent_classifier_agent = IntentClassifier()


    # Initialize orchestrator
    orchestrator = Orchestrator(
        rephraser=rephraser_agent,
        retriever=retriever_agent,
        generator=generator_agent,
        evaluator=evaluator_agent,
        intent_classifier=intent_classifier_agent,
        jira_adapter=jira_adapter
    )

    print("\n--- 3. RUNNING THE AGENTIC RAG WORKFLOW ---")
    result_state = orchestrator.run(query)

    print("\n--- 4. WORKFLOW FINISHED ---")
    final_node_state = result_state.get('evaluator', {})
    final_answer = final_node_state.get('final_answer')

    if final_answer:
        print("\n?? Final Answer:")
        print(final_answer)
    else:
        print("\n? Could not retrieve a final answer.")
        print("Final state:", result_state)


if __name__ == "__main__":
    load_dotenv()

    print("Welcome to the Agentic RAG Assistant! ??")
    print("Type your question below. Type 'exit' to quit.\n")

    while True:
        user_query = input("?? You: ")
        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye! ??")
            break
        setup_and_run(user_query)

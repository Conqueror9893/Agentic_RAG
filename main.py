from src.agents.orchestrator import Orchestrator
from src.agents.retriever import Retriever
from src.agents.generator import Generator
from src.agents.rephraser import Rephraser
from src.agents.evaluator import Evaluator
from src.tools.file_loader import load_documents
from src.tools.vector_store import get_vector_store, add_documents_to_store
from src.tools.github_adapter import GitHubAdapter
import os

def setup_and_run(query: str, github_repo_url: str = ""):
    """
    Sets up the RAG system, ingests data, and runs the query using Ollama and sentence-transformers.
    """
    print("--- 1. CONFIGURATION AND SETUP ---")
    print("Using local Ollama and sentence-transformers setup.")

    print("\n--- 2. DOCUMENT INGESTION ---")
    documents = load_documents("./data")
    if not documents:
        print("No documents found in the './data' directory. Please add some .txt files and try again.")
        return

    vector_store = get_vector_store()
    if documents:
        add_documents_to_store(vector_store, documents)

    print("\n--- 3. AGENT AND ORCHESTRATOR INITIALIZATION ---")
    github_adapter = GitHubAdapter()
    rephraser_agent = Rephraser()
    retriever_agent = Retriever(vector_store=vector_store, github_adapter=github_adapter)
    generator_agent = Generator()
    evaluator_agent = Evaluator()

    orchestrator = Orchestrator(
        rephraser=rephraser_agent,
        retriever=retriever_agent,
        generator=generator_agent,
        evaluator=evaluator_agent
    )

    print("\n--- 4. RUNNING THE AGENTIC RAG WORKFLOW ---")
    print(f"DEBUG: Running with GitHub repo URL → {github_repo_url}")
    result_state = orchestrator.run(query, github_repo_url=github_repo_url)

    print("\n--- 5. WORKFLOW FINISHED ---")
    final_node_state = result_state.get('evaluator', {})
    final_answer = final_node_state.get('final_answer')

    if final_answer:
        print("\nFinal Answer:")
        print(final_answer)
    else:
        print("\nCould not retrieve a final answer.")
        print("Final state:", result_state)


if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.makedirs("./data")
    if not os.path.exists("./data/sample.txt"):
        with open("./data/sample.txt", "w") as f:
            f.write("The capital of France is Paris. The Eiffel Tower is a famous landmark in Paris. The currency of Japan is the Yen.")

    user_query = input("Please enter your query: ")
    github_repo = input("Enter a GitHub repo URL to include context from (or press Enter to skip): ")
    print(f"DEBUG: Running with GitHub repo URL → {github_repo}")

    if user_query and user_query.strip():
        clean_repo_url = github_repo.strip() or None
        setup_and_run(user_query.strip(), github_repo_url=clean_repo_url)
        # setup_and_run(user_query.strip(), github_repo.strip())
    else:
        print("No query entered. Exiting.")

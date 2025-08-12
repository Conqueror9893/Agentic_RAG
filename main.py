import os
import argparse
import config
from src.agents.orchestrator import Orchestrator
from src.agents.retriever import Retriever
from src.agents.generator import Generator
from src.agents.rephraser import Rephraser
from src.agents.evaluator import Evaluator
from src.tools.file_loader import load_documents
from src.adaptors.outlook import OutlookAdaptor
from src.tools.vector_store import get_vector_store, add_documents_to_store

def setup_and_run(query: str, source: str = "file", max_emails: int = 10):
    """
    Sets up the RAG system, ingests data from the specified source, and runs the query.
    """
    print("--- 1. CONFIGURATION AND SETUP ---")
    print(f"Using data source: {source}")

    print("\n--- 2. DOCUMENT INGESTION ---")
    documents = []
    if source == "file":
        documents = load_documents("./data")
        if not documents:
            print("No documents found in the './data' directory. Please add some files and try again.")
            return
    elif source == "outlook":
        required_configs = [
            config.OUTLOOK_CLIENT_ID,
            config.OUTLOOK_CLIENT_SECRET,
            config.OUTLOOK_TENANT_ID,
            config.OUTLOOK_USER_PRINCIPAL_NAME
        ]
        if not all(required_configs):
            print("Outlook credentials not fully configured in config.py. Please set them up.")
            return

        outlook_adaptor = OutlookAdaptor(
            client_id=config.OUTLOOK_CLIENT_ID,
            client_secret=config.OUTLOOK_CLIENT_SECRET,
            tenant_id=config.OUTLOOK_TENANT_ID,
            user_principal_name=config.OUTLOOK_USER_PRINCIPAL_NAME
        )
        documents = outlook_adaptor.load_documents(max_emails=max_emails)
        if not documents:
            print("No documents loaded from Outlook.")
            return
    else:
        print(f"Unknown data source: {source}")
        return

    vector_store = get_vector_store()
    if documents:
        add_documents_to_store(vector_store, documents)

    print("\n--- 3. AGENT AND ORCHESTRATOR INITIALIZATION ---")
    rephraser_agent = Rephraser()
    retriever_agent = Retriever(vector_store=vector_store)
    generator_agent = Generator()
    evaluator_agent = Evaluator()

    orchestrator = Orchestrator(
        rephraser=rephraser_agent,
        retriever=retriever_agent,
        generator=generator_agent,
        evaluator=evaluator_agent
    )

    print("\n--- 4. RUNNING THE AGENTIC RAG WORKFLOW ---")
    result_state = orchestrator.run(query)

    print("\n--- 5. WORKFLOW FINISHED ---")
    # The final state is nested under the last node that ran
    final_node_state = result_state.get('evaluator', {})
    final_answer = final_node_state.get('final_answer')

    if final_answer:
        print("\nFinal Answer:")
        print(final_answer)
    else:
        print("\nCould not retrieve a final answer.")
        print("Final state:", result_state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic RAG Q&A System")
    parser.add_argument("query", type=str, help="The query to ask the system.")
    parser.add_argument("--source", type=str, default="file", choices=["file", "outlook"],
                        help="The data source to use for ingestion (default: file).")
    parser.add_argument("--max_emails", type=int, default=20,
                        help="The maximum number of emails to fetch from Outlook (default: 20).")
    args = parser.parse_args()

    # Ensure the data directory exists if using the file source
    if args.source == "file" and not os.path.exists("./data"):
        os.makedirs("./data")
        print("Created './data' directory. Please add documents to it.")

    if args.query and args.query.strip():
        setup_and_run(args.query, source=args.source, max_emails=args.max_emails)
    else:
        print("No query entered. Exiting.")

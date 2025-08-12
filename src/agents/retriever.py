from typing import List, Optional
from src.tools.vector_store import VectorStore
from src.tools.github_adapter import GitHubAdapter
from config import USE_GITHUB_CONTEXT

class Retriever:
    """
    This agent retrieves relevant documents from the vector store and optionally from a GitHub repository.
    """
    def __init__(self, vector_store: VectorStore, github_adapter: Optional[GitHubAdapter] = None):
        """
        Initializes the Retriever.

        Args:
            vector_store: The vector store to retrieve documents from.
            github_adapter: An optional GitHubAdapter instance to fetch data from GitHub.
        """
        self.vector_store = vector_store
        self.github_adapter = github_adapter

    def retrieve(self, queries: List[str], k: int = 2, github_repo_url: Optional[str] = None) -> List[str]:
        """
        Retrieves documents for the given queries from the vector store and a GitHub repo if specified.

        Args:
            queries: A list of queries to search for.
            k: The number of documents to retrieve for each query from the vector store.
            github_repo_url: Optional URL of a GitHub repository to fetch context from.

        Returns:
            A list of unique retrieved document contents.
        """
        print(f"Retrieving documents for queries: {queries}")
        print(f"USE_GITHUB_CONTEXT: {USE_GITHUB_CONTEXT}")
        print(f"github_adapter: {self.github_adapter is not None}")
        print(f"github_repo_url: {github_repo_url}")

        # 1. Retrieve from vector store
        retrieved_docs = []
        for query in queries:
            # Assuming similarity_search returns objects with a page_content attribute
            docs = self.vector_store.similarity_search(query, k=k)
            retrieved_docs.extend(docs)

        # Get unique documents by their content
        unique_docs_by_content = {doc.page_content for doc in retrieved_docs}

        # 2. Retrieve from GitHub if enabled and specified
        if USE_GITHUB_CONTEXT and self.github_adapter and github_repo_url:
            print(f"Fetching additional context from GitHub repository: {github_repo_url}")
            repo_info = self.github_adapter._parse_repo_url(github_repo_url)

            if repo_info:
                owner, repo = repo_info['owner'], repo_info['repo']

                # Fetch README
                readme = self.github_adapter.fetch_repo_file(owner, repo, "README.md")
                if readme:
                    unique_docs_by_content.add(readme)

                # Fetch open issues
                issues = self.github_adapter.fetch_issues(owner, repo, state="open")
                unique_docs_by_content.update(issues)

                # Fetch recent commits
                commits = self.github_adapter.fetch_commits(owner, repo)
                unique_docs_by_content.update(commits)
            else:
                print(f"Warning: Could not parse GitHub URL: {github_repo_url}")

        print(f"Retrieved {len(unique_docs_by_content)} unique documents in total.")

        return list(unique_docs_by_content)

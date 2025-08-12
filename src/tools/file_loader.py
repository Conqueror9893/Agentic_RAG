# from langchain_community.document_loaders import DirectoryLoader, TextLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# def load_documents(directory_path: str = "./data"):
#     """
#     Loads documents from the specified directory, splits them into chunks, and returns them.
#     """
#     print(f"Loading documents from {directory_path}...")
#     loader = DirectoryLoader(directory_path, glob="**/*.txt", loader_cls=TextLoader)
#     documents = loader.load()

#     if not documents:
#         print("No documents found.")
#         return []

#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     chunked_documents = text_splitter.split_documents(documents)

#     print(f"Loaded and split {len(documents)} documents into {len(chunked_documents)} chunks.")

#     return chunked_documents

# if __name__ == "__main__":
#     # This is for testing the file loader in isolation.
#     # First, let's create a dummy file in the data directory.
#     import os
#     if not os.path.exists("./data"):
#         os.makedirs("./data")
#     with open("./data/sample.txt", "w") as f:
#         f.write("This is a sample document about LangChain and LangGraph. " * 100)
#         f.write("\n\n")
#         f.write("This is another paragraph in the same document. " * 100)

#     docs = load_documents()
#     print(f"Successfully loaded {len(docs)} chunks.")
#     print("First chunk:")
#     print(docs[0].page_content)
#     print("\nMetadata:")
#     print(docs[0].metadata)


# src/tools/jira_loader.py

import os
import requests
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")  # https://your-domain.atlassian.net
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


class JiraLoader:
    def __init__(self):
        if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
            raise ValueError("Missing JIRA credentials in environment variables.")
        self.base_url = JIRA_URL
        self.auth = (JIRA_USERNAME, JIRA_API_TOKEN)
        self.headers = {"Accept": "application/json"}

    def _split_text(self, text: str, metadata: dict) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return splitter.create_documents([text], metadatas=[metadata])

    def load_ticket(self, ticket_id: str) -> list[Document]:
        url = f"{self.base_url}/rest/api/3/issue/{ticket_id}"
        response = requests.get(url, headers=self.headers, auth=self.auth)

        if response.status_code != 200:
            print(f"Failed to fetch Jira ticket {ticket_id}: {response.status_code}")
            return []

        data = response.json()
        fields = data["fields"]
        summary = fields.get("summary", "")
        description = self._parse_description(fields.get("description"))
        assignee = fields.get("assignee", {}).get("emailAddress", "Unassigned")
        reporter = fields.get("reporter", {}).get("emailAddress", "Unknown")
        status = fields.get("status", {}).get("name", "Unknown")
        labels = fields.get("labels", [])

        full_text = f"""
            Issue: {ticket_id}
            Summary: {summary}
            Status: {status}
            Assignee: {assignee}
            Reporter: {reporter}
            Labels: {', '.join(labels)}
            Description:
            {description}
            """.strip()

        return self._split_text(full_text, {"ticket_id": ticket_id})


    def load_comments(self, ticket_id: str) -> list[Document]:
        url = f"{self.base_url}/rest/api/3/issue/{ticket_id}/comment"
        response = requests.get(url, headers=self.headers, auth=self.auth)

        if response.status_code != 200:
            print(f"Failed to fetch comments for {ticket_id}")
            return []

        comments = response.json().get("comments", [])
        all_text = "\n\n".join(
            [f"{c['author']['displayName']} said:\n{c['body']['content'][0]['content'][0].get('text', '')}" for c in comments]
        )

        return self._split_text(all_text, {"ticket_id": ticket_id, "type": "comments"})

    def load_tickets(self, jql: str, max_results=10) -> list[Document]:
        url = f"{self.base_url}/rest/api/3/search"
        params = {"jql": jql, "maxResults": max_results}
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)

        if response.status_code != 200:
            print(f"Failed to search Jira: {response.status_code}")
            return []

        issues = response.json().get("issues", [])
        docs = []

        for issue in issues:
            ticket_id = issue["key"]
            summary = issue["fields"].get("summary", "")
            description = self._parse_description(issue["fields"].get("description"))
            full_text = f"Issue: {ticket_id}\nSummary: {summary}\n\nDescription:\n{description}"
            docs.extend(self._split_text(full_text, {"ticket_id": ticket_id}))

        return docs

    def _parse_description(self, description) -> str:
        if not description or "content" not in description:
            return ""
        parts = []
        for block in description["content"]:
            for content in block.get("content", []):
                parts.append(content.get("text", ""))
        return "\n".join(parts)

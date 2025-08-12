# # import os
# # from langchain.docstore.document import Document
# # from langchain_text_splitters import RecursiveCharacterTextSplitter
# # from src.tools.jira_loader import JiraLoader

# # class JiraAdapter:
# #     """
# #     An adapter to connect Jira as a data source for the agentic RAG system.
# #     This class uses the JiraLoader to fetch data from Jira and transforms it
# #     into a format that can be used by the vector store.
# #     """
# #     def __init__(self, jira_loader: JiraLoader):
# #         """
# #         Initializes the JiraAdapter with a JiraLoader instance.
# #         """
# #         self.jira_loader = jira_loader

# #     def load_and_split(self, project_key: str, user_email: str) -> list[Document]:
# #         """
# #         Fetches all relevant data from Jira for a given project and user,
# #         and splits it into chunks.
# #         """
# #         print(f"Fetching Jira data for project '{project_key}' and user '{user_email}'...")

# #         # Fetch all tickets for the user
# #         user_tickets_str = self.jira_loader.get_user_tickets(user_email)

# #         # In a real-world scenario, you might want to fetch other data as well,
# #         # such as project status, worklogs, comments, etc.
# #         # For now, we'll just use the user's tickets as the data source.

# #         if not user_tickets_str or "No tickets found" in user_tickets_str:
# #             print("No documents to load from Jira.")
# #             return []

# #         # Convert the string data into a LangChain Document
# #         # We use a single document for all the tickets, but you could also
# #         # create one document per ticket.
# #         documents = [Document(page_content=user_tickets_str, metadata={"source": "jira"})]

# #         # Split the document into smaller chunks
# #         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# #         chunked_documents = text_splitter.split_documents(documents)

# #         print(f"Loaded and split Jira data into {len(chunked_documents)} chunks.")

# #         return chunked_documents

# # if __name__ == '__main__':
# #     # This is for testing the Jira adapter in isolation.
# #     # Note: To run this, you need to have a .env file with your JIRA credentials.
# #     from config import JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN

# #     if all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
# #         try:
# #             jira_loader = JiraLoader()
# #             jira_adapter = JiraAdapter(jira_loader)

# #             # Replace with a real project key and user email for testing
# #             project_key = "PROJ"  # e.g., "MYPROJ"
# #             user_email = "test@example.com"  # e.g., "user@yourdomain.com"

# #             docs = jira_adapter.load_and_split(project_key, user_email)
# #             if docs:
# #                 print(f"Successfully loaded {len(docs)} chunks from Jira.")
# #                 print("First chunk:")
# #                 print(docs[0].page_content)
# #                 print("\nMetadata:")
# #                 print(docs[0].metadata)
# #             else:
# #                 print("No data was loaded from Jira.")

# #         except ValueError as e:
# #             print(f"Error: {e}")
# #         except Exception as e:
# #             print(f"An unexpected error occurred: {e}")
# #     else:
# #         print("Jira credentials not found in .env file. Skipping JiraAdapter test.")


# # import requests
# # from langchain.schema import Document
# # import os
# # from dotenv import load_dotenv

# # load_dotenv()

# # class JiraAdapter:
# #     def __init__(self):
# #         self.base_url = "https://appzillon.atlassian.net"
# #         self.api_token = os.getenv("JIRA_API_TOKEN")

# #     def load_ticket(self, ticket_id, user_email):
# #         url = f"{self.base_url}/rest/api/3/issue/{ticket_id}"
# #         auth = (user_email, self.api_token)
# #         headers = {"Accept": "application/json"}

# #         response = requests.get(url, headers=headers, auth=auth)
# #         if response.status_code != 200:
# #             print(f"Failed to fetch Jira ticket: {response.status_code} {response.text}")
# #             return []

# #         data = response.json()
# #         fields = data.get("fields", {})
# #         summary = fields.get("summary", "")
# #         description = fields.get("description", {}).get("content", [])

# #         content = summary + "\n" + self._parse_description(description)

# #         return [Document(page_content=content, metadata={"ticket_id": ticket_id})]

# #     def _parse_description(self, description_blocks):
# #         text = ""
# #         for block in description_blocks:
# #             for p in block.get("content", []):
# #                 text += p.get("text", "") + "\n"
# #         return text


# # src/tools/jira_adapter.py

# from src.tools.jira_loader import JiraLoader
# from typing import Dict, Any
# class JiraAdapter:
#     def __init__(self, jira_loader=None):
#         self.jira_loader = jira_loader or JiraLoader()

#     def load_ticket(self, ticket_id: str, user_email: str = None):
#         return self.jira_loader.load_ticket(ticket_id)

#     def load_comments(self, ticket_id: str):
#         return self.jira_loader.load_comments(ticket_id)

#     def load_by_jql(self, jql: str):
#         return self.jira_loader.load_tickets(jql)

#     def load_and_split(self, project_key: str, user_email: str = None):
#         # You can customize the JQL based on your needs
#         jql = f'project = "{project_key}" ORDER BY created DESC'
#         return self.jira_loader.load_tickets(jql)
    
#     def fetch_all_issues_with_details(self, project_key: str) -> list[Dict[str, Any]]:
#         return self.jira_loader.get_issues_in_project(project_key)


import requests

class JiraAdapter:
    def __init__(self, jira_loader: str, api_token: str, email: str, project_key: str):
        self.loader = jira_loader
        self.api_token = api_token
        self.email = email
        self.project_key = project_key
        self.headers = {
            "Authorization": f"Basic {self._encode_auth()}",
            "Content-Type": "application/json",
        }

    def _encode_auth(self):
        import base64
        auth_str = f"{self.email}:{self.api_token}"
        return base64.b64encode(auth_str.encode()).decode()

    def fetch_all_issues_with_details(self):
        print(f"Fetching issues for project: {self.project_key}")
        start_at = 0
        max_results = 50
        issues = []

        while True:
            url = (
                f"{self.loader}/rest/api/3/search"
                f"?jql=project={self.project_key}"
                f"&startAt={start_at}&maxResults={max_results}"
                f"&expand=renderedFields"
            )
            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                print(f"Jira API call failed: {response.status_code}, {response.text}")
                break

            data = response.json()
            fetched = data.get("issues", [])

            for issue in fetched:
                enriched = self._parse_issue(issue)
                if enriched:
                    issues.append(enriched)

            if len(fetched) < max_results:
                break
            start_at += max_results

        print(f"Total issues fetched: {len(issues)}")
        return issues

    def _parse_issue(self, issue):
        fields = issue.get("fields", {})
        return {
            "key": issue.get("key"),
            "summary": fields.get("summary", ""),
            "description": fields.get("description", ""),
            "status": fields.get("status", {}).get("name", ""),
            "priority": fields.get("priority", {}).get("name", ""),
            "issuetype": fields.get("issuetype", {}).get("name", ""),
            "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
            "reporter": (fields.get("reporter") or {}).get("displayName", "Unknown"),
            "created": fields.get("created", ""),
            "updated": fields.get("updated", ""),
            "labels": fields.get("labels", []),
            "subtasks": [
                {
                    "key": sub.get("key"),
                    "summary": sub.get("fields", {}).get("summary", ""),
                    "status": sub.get("fields", {}).get("status", {}).get("name", ""),
                }
                for sub in fields.get("subtasks", [])
            ],
        }

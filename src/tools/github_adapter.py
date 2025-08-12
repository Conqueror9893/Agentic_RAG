import os
import re
import base64
import requests
from typing import List, Dict, Optional

class GitHubAdapter:
    """
    Adapter for interacting with GitHub REST API.
    Fetches files, issues, commits, and repo metadata.
    """

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_API_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def _parse_repo_url(self, repo_url: str) -> Optional[Dict[str, str]]:
        match = re.match(r"https?://github\.com/([^/]+)/([^/]+)", repo_url)
        if match:
            return {"owner": match.group(1), "repo": match.group(2)}
        return None

    def fetch_repo_file(self, owner: str, repo: str, file_path: str = "README.md") -> Optional[str]:
        # Fetch all contents of the repo root
        url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        files = response.json()
        for file in files:
            if file["name"].lower() == file_path.lower():
                file_url = file["download_url"]
                file_response = requests.get(file_url)
                file_response.raise_for_status()
                return file_response.text
        return None


    def fetch_issues(self, owner: str, repo: str, state: str = "open") -> List[str]:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state={state}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            issues = response.json()
            return [f"Issue: {issue['title']}\n{issue.get('body', '')}" for issue in issues if 'pull_request' not in issue]
        except Exception as e:
            print(f"Error fetching issues: {e}")
            return []

    def fetch_commits(self, owner: str, repo: str) -> List[str]:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            commits = response.json()
            return [
                f"{c['commit']['message']}\nAuthor: {c['commit']['author']['name']}, Date: {c['commit']['author']['date']}"
                for c in commits
            ]
        except Exception as e:
            print(f"Error fetching commits: {e}")
            return []

    def fetch_repo_metadata(self, owner: str, repo: str) -> Optional[str]:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("description", "")
        except Exception as e:
            print(f"Error fetching repo metadata: {e}")
            return None

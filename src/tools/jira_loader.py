import os
from atlassian import Jira
from config import JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN

class JiraLoader:
    """
    A tool for interacting with Jira, allowing for fetching project details, issue statuses,
    and user contributions.
    """
    def __init__(self):
        """
        Initializes the JiraLoader by connecting to the Jira API using credentials
        from the environment.
        """
        if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
            raise ValueError(
                "Jira credentials (JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN) not found in environment. "
                "Please add them to your .env file."
            )

        self.jira = Jira(
            url=JIRA_URL,
            username=JIRA_USERNAME,
            password=JIRA_API_TOKEN,
            cloud=True
        )

    def get_project_status(self, project_key: str) -> str:
        """
        Retrieves the status of a given Jira project.
        """
        try:
            project = self.jira.project(project_key)
            return f"Project '{project['name']}' ({project['key']}) is currently in status: {project['projectCategory']['name']}."
        except Exception as e:
            return f"Error fetching project status for '{project_key}': {e}"

    def get_user_worklogs(self, project_key: str, user_email: str) -> str:
        """
        Retrieves the worklogs for a specific user on a given project.
        """
        jql_query = f'project = "{project_key}" AND worklogAuthor = "{user_email}"'
        try:
            issues = self.jira.jql(jql_query, fields="summary,worklog")
            total_time_spent_seconds = 0
            for issue in issues.get('issues', []):
                for worklog in issue['fields']['worklog']['worklogs']:
                    if worklog['author']['emailAddress'] == user_email:
                        total_time_spent_seconds += worklog['timeSpentSeconds']

            hours, remainder = divmod(total_time_spent_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"User {user_email} has logged {int(hours)} hours and {int(minutes)} minutes on project {project_key}."
        except Exception as e:
            return f"Error fetching worklogs for user '{user_email}' on project '{project_key}': {e}"

    def get_user_tickets(self, user_email: str) -> str:
        """
        Retrieves the tickets currently assigned to a specific user.
        """
        jql_query = f'assignee = "{user_email}" ORDER BY updated DESC'
        try:
            issues = self.jira.jql(jql_query, fields="summary,status")
            if not issues.get('issues'):
                return f"No tickets found for user {user_email}."

            ticket_list = [
                f"- {issue['key']}: {issue['fields']['summary']} (Status: {issue['fields']['status']['name']})"
                for issue in issues['issues']
            ]
            return f"Tickets for {user_email}:\n" + "\n".join(ticket_list)
        except Exception as e:
            return f"Error fetching tickets for user '{user_email}': {e}"


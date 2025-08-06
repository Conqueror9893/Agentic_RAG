import os
from atlassian import Jira
from config import JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN
from typing import Dict, Any

class JiraAdapter:
    """
    A tool for interacting with Jira, allowing for fetching project details, issue statuses,
    and user contributions.
    """
    def __init__(self, project_key: str):
        """
        Initializes the JiraAdapter by connecting to the Jira API using credentials
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
        self.project_key = project_key

    def get_project_status(self) -> str:
        """
        Retrieves the status of the configured Jira project.
        """
        try:
            project = self.jira.project(self.project_key)
            return f"Project '{project['name']}' ({project['key']}) is currently in status: {project['projectCategory']['name']}."
        except Exception as e:
            return f"Error fetching project status for '{self.project_key}': {e}"

    def get_user_worklogs(self, user_email: str) -> str:
        """
        Retrieves the worklogs for a specific user on the configured project.
        """
        jql_query = f'project = "{self.project_key}" AND worklogAuthor = "{user_email}"'
        try:
            issues = self.jira.jql(jql_query, fields="summary,worklog")
            total_time_spent_seconds = 0
            for issue in issues.get('issues', []):
                for worklog in issue['fields']['worklog']['worklogs']:
                    if worklog['author']['emailAddress'] == user_email:
                        total_time_spent_seconds += worklog['timeSpentSeconds']

            hours, remainder = divmod(total_time_spent_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"User {user_email} has logged {int(hours)} hours and {int(minutes)} minutes on project {self.project_key}."
        except Exception as e:
            return f"Error fetching worklogs for user '{user_email}' on project '{self.project_key}': {e}"

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

    def get_issues_in_project(self) -> list[Dict[str, Any]]:
        jql = f'project = {self.project_key}'
        issues = self.jira.jql(jql)['issues']
        return [self._enrich_issue(issue['key']) for issue in issues]

    def _enrich_issue(self, issue_key: str) -> Dict[str, Any]:
        issue = self.jira.issue(issue_key)

        enriched = {
            "key": issue["key"],
            "summary": issue["fields"].get("summary"),
            "description": issue["fields"].get("description"),
            "status": issue["fields"].get("status", {}).get("name"),
            "assignee": issue["fields"].get("assignee", {}).get("emailAddress"),
            "reporter": issue["fields"].get("reporter", {}).get("emailAddress"),
            "created": issue["fields"].get("created"),
            "updated": issue["fields"].get("updated"),
            "duedate": issue["fields"].get("duedate"),
            "labels": issue["fields"].get("labels", []),
            "priority": issue["fields"].get("priority", {}).get("name"),
            "issuetype": issue["fields"].get("issuetype", {}).get("name"),
            "subtasks": [
                {
                    "key": sub["key"],
                    "summary": sub["fields"]["summary"],
                    "status": sub["fields"]["status"]["name"]
                }
                for sub in issue["fields"].get("subtasks", [])
            ],
        }

        return enriched

    def get_tickets_by_assignee(self, assignee_email: str) -> str:
        """
        Retrieves the number of tickets assigned to a specific user.
        """
        jql_query = f'project = "{self.project_key}" AND assignee = "{assignee_email}"'
        try:
            issues = self.jira.jql(jql_query)
            return f"User {assignee_email} has {issues['total']} tickets assigned."
        except Exception as e:
            return f"Error fetching tickets for user '{assignee_email}': {e}"

    def get_ticket_status(self, ticket_key: str) -> str:
        """
        Retrieves the status of a specific ticket.
        """
        try:
            issue = self.jira.issue(ticket_key, fields="status")
            status = issue['fields']['status']['name']
            return f"Ticket {ticket_key} is in status: {status}."
        except Exception as e:
            return f"Error fetching status for ticket '{ticket_key}': {e}"

    def get_ticket_count_by_status(self, status: str) -> str:
        """
        Retrieves the number of tickets in a specific status.
        """
        jql_query = f'project = "{self.project_key}" AND status = "{status}"'
        try:
            issues = self.jira.jql(jql_query)
            return f"There are {issues['total']} tickets in '{status}' status."
        except Exception as e:
            return f"Error fetching ticket count for status '{status}': {e}"

    def get_tickets_not_updated_since(self, hours: int) -> str:
        """
        Retrieves tickets that have not been updated in the last X hours.
        """
        jql_query = f'project = "{self.project_key}" AND updated <= -{hours}h'
        try:
            issues = self.jira.jql(jql_query, fields="summary,status,updated")
            if not issues.get('issues'):
                return f"No tickets found that have not been updated in the last {hours} hours."

            ticket_list = [
                f"- {issue['key']}: {issue['fields']['summary']} (Status: {issue['fields']['status']['name']}, Last Updated: {issue['fields']['updated']})"
                for issue in issues['issues']
            ]
            return f"Tickets not updated in the last {hours} hours:\n" + "\n".join(ticket_list)
        except Exception as e:
            return f"Error fetching tickets not updated since {hours} hours ago: {e}"

    def get_tickets_updated_by_others(self, user_email: str) -> str:
        """
        Retrieves tickets assigned to a user that were last updated by someone else.
        This is a conceptual method. A direct JQL for this is not available.
        We can fetch recent tickets and check the author of the last comment.
        This implementation is a simplified version.
        """
        jql_query = f'project = "{self.project_key}" AND assignee = "{user_email}" ORDER BY updated DESC'
        try:
            issues = self.jira.jql(jql_query, fields="summary,comment", expand="changelog")
            updated_by_others = []
            for issue in issues.get('issues', []):
                comments = self.jira.issue_comments(issue['key'])
                if comments['comments']:
                    last_comment = comments['comments'][-1]
                    if last_comment['author']['emailAddress'] != user_email:
                        updated_by_others.append(f"- {issue['key']}: {issue['fields']['summary']} (Last comment by: {last_comment['author']['displayName']})")

            if not updated_by_others:
                return f"No tickets found for {user_email} that were recently updated by others."

            return f"Tickets for {user_email} updated by others:\n" + "\n".join(updated_by_others)
        except Exception as e:
            return f"Error fetching tickets updated by others for user '{user_email}': {e}"


    def get_tickets_with_approaching_deadlines(self, days: int) -> str:
        """
        Retrieves tickets with due dates in the next X days.
        """
        jql_query = f'project = "{self.project_key}" AND due >= now() AND due <= "{days}d"'
        try:
            issues = self.jira.jql(jql_query, fields="summary,status,duedate")
            if not issues.get('issues'):
                return f"No tickets found with deadlines in the next {days} days."

            ticket_list = [
                f"- {issue['key']}: {issue['fields']['summary']} (Status: {issue['fields']['status']['name']}, Due: {issue['fields']['duedate']})"
                for issue in issues['issues']
            ]
            return f"Tickets with approaching deadlines ({days} days):\n" + "\n".join(ticket_list)
        except Exception as e:
            return f"Error fetching tickets with approaching deadlines: {e}"

    def get_tickets_stagnant_in_status(self, days: int) -> str:
        """
        Retrieves tickets that have not changed status in the last X days.
        """
        jql_query = f'project = "{self.project_key}" AND status changed BEFORE "-{days}d"'
        try:
            issues = self.jira.jql(jql_query, fields="summary,status,statuscategorychangedate")
            if not issues.get('issues'):
                return f"No tickets found that have been stagnant for the last {days} days."

            ticket_list = [
                f"- {issue['key']}: {issue['fields']['summary']} (Status: {issue['fields']['status']['name']}, Last Status Change: {issue['fields']['statuscategorychangedate']})"
                for issue in issues['issues']
            ]
            return f"Stagnant tickets (not changed status in {days} days):\n" + "\n".join(ticket_list)
        except Exception as e:
            return f"Error fetching stagnant tickets: {e}"

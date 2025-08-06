from src.tools.jira_adapter import JiraAdapter

def get_tickets_by_assignee(jira_adapter: JiraAdapter, assignee_email: str) -> str:
    """
    Tool to get the number of tickets assigned to a specific user.
    """
    return jira_adapter.get_tickets_by_assignee(assignee_email)

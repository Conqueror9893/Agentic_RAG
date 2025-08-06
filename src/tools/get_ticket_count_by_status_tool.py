from src.tools.jira_adapter import JiraAdapter

def get_ticket_count_by_status(jira_adapter: JiraAdapter, status: str) -> str:
    """
    Tool to get the number of tickets in a specific status.
    """
    return jira_adapter.get_ticket_count_by_status(status)

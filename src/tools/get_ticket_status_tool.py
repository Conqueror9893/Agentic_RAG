from src.tools.jira_adapter import JiraAdapter

def get_ticket_status(jira_adapter: JiraAdapter, ticket_key: str) -> str:
    """
    Tool to get the status of a specific ticket.
    """
    return jira_adapter.get_ticket_status(ticket_key)

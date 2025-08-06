from src.tools.jira_adapter import JiraAdapter

def get_tickets_not_updated_since(jira_adapter: JiraAdapter, hours: int) -> str:
    """
    Tool to get tickets that have not been updated in the last X hours.
    """
    return jira_adapter.get_tickets_not_updated_since(hours)

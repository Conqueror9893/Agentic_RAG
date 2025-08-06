from src.tools.jira_adapter import JiraAdapter

def get_tickets_stagnant_in_status(jira_adapter: JiraAdapter, days: int) -> str:
    """
    Tool to get tickets that have not changed status in the last X days.
    """
    return jira_adapter.get_tickets_stagnant_in_status(days)

from src.tools.jira_adapter import JiraAdapter

def get_tickets_updated_by_others(jira_adapter: JiraAdapter, user_email: str) -> str:
    """
    Tool to get tickets assigned to a user that were last updated by someone else.
    """
    return jira_adapter.get_tickets_updated_by_others(user_email)

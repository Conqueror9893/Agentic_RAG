from src.tools.jira_adapter import JiraAdapter

def get_tickets_with_approaching_deadlines(jira_adapter: JiraAdapter, days: int) -> str:
    """
    Tool to get tickets with due dates in the next X days.
    """
    return jira_adapter.get_tickets_with_approaching_deadlines(days)

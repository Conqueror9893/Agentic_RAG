from typing import Literal
from src.tools.llm_interface import run_ollama_model

class IntentClassifier:
    """
    Classifies user intent using an LLM.
    """
    
    def classify(self, query: str) -> Literal[
        "GET_TICKETS_BY_ASSIGNEE",
        "GET_TICKET_STATUS",
        "GET_TICKET_COUNT_BY_STATUS",
        "GET_TICKETS_NOT_UPDATED_SINCE",
        "GET_TICKETS_UPDATED_BY_OTHERS",
        "GET_TICKETS_WITH_APPROACHING_DEADLINES",
        "GET_TICKETS_STAGNANT_IN_STATUS",
        "KNOWLEDGE_QUERY",
        "OTHER"
    ]:
        prompt = f"""
You are an intent classification agent for a Jira assistant. Classify the user's query into one of the following intents:

- GET_TICKETS_BY_ASSIGNEE: User is asking for the number of tickets assigned to a person.
  (e.g., "how many tickets are assigned to john.doe@example.com?", "show me john's tickets")
- GET_TICKET_STATUS: User is asking for the status of a specific ticket.
  (e.g., "what's the status of ticket PSA-123?", "where is PSA-123 at?")
- GET_TICKET_COUNT_BY_STATUS: User is asking for the number of tickets in a particular status.
  (e.g., "how many tickets are in 'In Progress' status?", "show me the count of open tickets")
- GET_TICKETS_NOT_UPDATED_SINCE: User is asking for tickets that have not been updated for a certain period.
  (e.g., "show me tickets not updated in the last 24 hours", "any stale tickets?")
- GET_TICKETS_UPDATED_BY_OTHERS: User is asking for their tickets that were updated by someone else.
  (e.g., "which of my tickets were updated by others?", "did anyone comment on my tickets?")
- GET_TICKETS_WITH_APPROACHING_DEADLINES: User is asking for tickets with upcoming due dates.
  (e.g., "show me tickets due in the next 5 days", "any tickets with approaching deadlines?")
- GET_TICKETS_STAGNANT_IN_STATUS: User is asking for tickets that have not changed status for a certain period.
  (e.g., "show me tickets that haven't changed status in a week", "any tickets stuck in the same status?")
- KNOWLEDGE_QUERY: The user is asking a general question that can be answered from a knowledge base.
  (e.g., "how to setup a local development environment?", "what is our policy on remote work?")
- OTHER: The user's query does not fit into any of the above categories.

Respond with only one intent label.

Query: "{query}"
"""
        response = run_ollama_model(prompt)
        return response.strip().split()[0]

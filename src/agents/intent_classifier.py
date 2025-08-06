# src/agents/intent_classifier.py

from typing import Literal
from src.tools.llm_interface import run_ollama_model

class IntentClassifier:
    """
    Classifies user intent using an LLM.
    """
    
    def classify(self, query: str) -> Literal["JIRA_QUERY", "KNOWLEDGE_QUERY", "OTHER"]:
        prompt = f"""
You are an intent classification agent. Classify the user's query into one of:
- JIRA_QUERY: related to tickets, bugs, issues, or workflows.
- KNOWLEDGE_QUERY: related to internal documentation, concepts, or reference info.
- OTHER: anything else.

Respond with only one label: JIRA_QUERY, KNOWLEDGE_QUERY, or OTHER.

Query: "{query}"
        """
        response = run_ollama_model(prompt)
        return response.strip().split()[0]

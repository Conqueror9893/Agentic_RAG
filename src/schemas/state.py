from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    """
    Represents the state of our agentic RAG system.
    This state is passed between the nodes of our LangGraph.
    """
    original_query: str
    intent: str
    rephrased_queries: Optional[List[str]]
    retrieved_documents: Optional[List[str]]
    generated_answer: Optional[str]
    is_answer_faithful: Optional[bool]
    is_answer_verified: Optional[bool]
    final_answer: Optional[str]

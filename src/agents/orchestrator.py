from langgraph.graph import StateGraph, END
from src.schemas.state import AgentState
from src.agents.retriever import Retriever
from src.agents.generator import Generator
from src.agents.rephraser import Rephraser
from src.agents.evaluator import Evaluator

class Orchestrator:
    """
    The orchestrator manages the overall workflow of the agentic RAG system.
    It defines the graph of agents and the transitions between them.
    """
    def __init__(self, rephraser: Rephraser, retriever: Retriever, generator: Generator, evaluator: Evaluator):
        self.rephraser = rephraser
        self.retriever = retriever
        self.generator = generator
        self.evaluator = evaluator
        self.workflow = self._build_workflow()

    def rephraser_node(self, state: AgentState) -> dict:
        print("---CALLING REPHRASER---")
        query = state['original_query']
        rephrased_queries = self.rephraser.rephrase(query)
        return {"rephrased_queries": rephrased_queries}

    def retriever_node(self, state: AgentState) -> dict:
        print("---CALLING RETRIEVER---")
        queries = state['rephrased_queries']
        github_repo_url = state.get("github_repo_url", None)
        print(f"DEBUG: Running with GitHub repo URL → {github_repo_url}")
        documents = self.retriever.retrieve(queries, k=2, github_repo_url=github_repo_url)
        return {"retrieved_documents": documents}

    def generator_node(self, state: AgentState) -> dict:
        print("---CALLING GENERATOR---")
        query = state['original_query']
        documents = state['retrieved_documents']
        generated_answer = self.generator.generate(query, documents)
        return {"generated_answer": generated_answer}

    def evaluator_node(self, state: AgentState) -> dict:
        print("---CALLING EVALUATOR---")
        query = state['original_query']
        documents = state['retrieved_documents']
        generated_answer = state['generated_answer']
        is_faithful = self.evaluator.evaluate(query, documents, generated_answer)
        final_answer = generated_answer if is_faithful else "I cannot provide a faithful answer based on the retrieved documents."
        return {"final_answer": final_answer, "is_answer_faithful": is_faithful}

    def _build_workflow(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("rephraser", self.rephraser_node)
        workflow.add_node("retriever", self.retriever_node)
        workflow.add_node("generator", self.generator_node)
        workflow.add_node("evaluator", self.evaluator_node)
        workflow.set_entry_point("rephraser")
        workflow.add_edge("rephraser", "retriever")
        workflow.add_edge("retriever", "generator")
        workflow.add_edge("generator", "evaluator")
        workflow.add_edge("evaluator", END)
        return workflow.compile()

    def run(self, query: str, github_repo_url: str = ""):
        """
        Runs the agentic RAG system with the given query and optional GitHub repo context.
        """
        print(f"DEBUG: Running with GitHub repo URL → {github_repo_url}")
        initial_state = {
            "original_query": query,
            "github_repo_url": github_repo_url if github_repo_url else None
        }

        final_state = None
        for s in self.workflow.stream(initial_state):
            print(f"---STATE UPDATE---\n{s}\n---END STATE UPDATE---")
            final_state = s
        return final_state

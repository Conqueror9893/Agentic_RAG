from langgraph.graph import StateGraph, END
from src.schemas.state import AgentState
from src.agents.retriever import Retriever
from src.agents.generator import Generator
from src.agents.rephraser import Rephraser
from src.agents.evaluator import Evaluator
from src.agents.intent_classifier import IntentClassifier

class Orchestrator:
    """
    The orchestrator manages the overall workflow of the agentic RAG system.
    It defines the graph of agents and the transitions between them.
    """
    def __init__(self, rephraser: Rephraser, retriever: Retriever, generator: Generator, evaluator: Evaluator, intent_classifier: IntentClassifier):
        self.rephraser = rephraser
        self.retriever = retriever
        self.generator = generator
        self.evaluator = evaluator
        self.intent_classifier = intent_classifier
        self.workflow = self._build_workflow()
    
    def intent_classifier_node(self, state: AgentState) -> dict:
        """Node that calls the Intent Classifier agent."""
        print("---CALLING INTENT CLASSIFIER---")
        query = state['original_query']
        intent = self.intent_classifier.classify(query)
        return {"intent": intent}

    def rephraser_node(self, state: AgentState) -> dict:
        """Node that calls the Rephraser agent."""
        print("---CALLING REPHRASER---")
        query = state['original_query']
        rephrased_queries = self.rephraser.rephrase(query)
        return {"rephrased_queries": rephrased_queries}

    def retriever_node(self, state: AgentState) -> dict:
        """Node that calls the Retriever agent."""
        print("---CALLING RETRIEVER---")
        queries = state['rephrased_queries']
        documents = self.retriever.retrieve(queries)
        return {"retrieved_documents": documents}

    def generator_node(self, state: AgentState) -> dict:
        """Node that calls the Generator agent."""
        print("---CALLING GENERATOR---")
        query = state['original_query']
        documents = state['retrieved_documents']
        generated_answer = self.generator.generate(query, documents)
        return {"generated_answer": generated_answer}

    def evaluator_node(self, state: AgentState) -> dict:
        """Node that calls the Evaluator agent."""
        print("---CALLING EVALUATOR---")
        query = state['original_query']
        documents = state['retrieved_documents']
        generated_answer = state['generated_answer']
        is_faithful = self.evaluator.evaluate(query, documents, generated_answer)

        final_answer = generated_answer if is_faithful else "I cannot provide a faithful answer based on the retrieved documents."
        return {"final_answer": final_answer, "is_answer_faithful": is_faithful}

    def _build_workflow(self):
        """Builds the LangGraph workflow for the agentic RAG system."""
        workflow = StateGraph(AgentState)

        workflow.add_node("intent_classifier", self.intent_classifier_node)
        workflow.add_node("rephraser", self.rephraser_node)
        workflow.add_node("retriever", self.retriever_node)
        workflow.add_node("generator", self.generator_node)
        workflow.add_node("evaluator", self.evaluator_node)

        workflow.set_entry_point("intent_classifier")
        workflow.add_edge("intent_classifier", "rephraser")
        workflow.add_edge("rephraser", "retriever")
        workflow.add_edge("retriever", "generator")
        workflow.add_edge("generator", "evaluator")
        workflow.add_edge("evaluator", END)

        return workflow.compile()

    def run(self, query: str):
        """Runs the JIRA agentic RAG system with the given query."""
        initial_state = {"original_query": query}
        final_state = None
        for s in self.workflow.stream(initial_state):
            print(f"---STATE UPDATE---\n{s}\n---END STATE UPDATE---")
            final_state = s
        return final_state

if __name__ == "__main__":
    from src.tools.vector_store import get_vector_store, add_documents_to_store
    from src.tools.file_loader import load_documents
    from src.agents.intent_classifier import IntentClassifier
    import os

    documents = load_documents("./data")
    if not documents:
        if not os.path.exists("./data"):
            os.makedirs("./data")
        with open("./data/sample.txt", "w") as f:
            f.write("The capital of France is Paris.")
        documents = load_documents("./data")

    vector_store = get_vector_store()
    if documents:
        add_documents_to_store(vector_store, documents)

    # Initialize agents
    rephraser_agent = Rephraser()
    retriever_agent = Retriever(vector_store=vector_store)
    generator_agent = Generator()
    evaluator_agent = Evaluator()
    intent_classifier_agent = IntentClassifier()

    orchestrator = Orchestrator(
        rephraser=rephraser_agent,
        retriever=retriever_agent,
        generator=generator_agent,
        evaluator=evaluator_agent,
        intent_classifier=intent_classifier_agent
    )

    result = orchestrator.run("What is the capital of France?")

    print("\n---ORCHESTRATOR FINISHED---")
    if result and 'final_answer' in result:
        print("Final Answer:")
        print(result['final_answer'])
    else:
        print("Could not retrieve a final answer.")
        print("Final state:", result)

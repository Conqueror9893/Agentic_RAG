import re
from langgraph.graph import StateGraph, END
from src.schemas.state import AgentState
from src.agents.retriever import Retriever
from src.agents.generator import Generator
from src.agents.rephraser import Rephraser
from src.agents.evaluator import Evaluator
from src.agents.intent_classifier import IntentClassifier
from src.tools.jira_adapter import JiraAdapter
from langchain.docstore.document import Document

# Import all the new tools
from src.tools.get_tickets_by_assignee_tool import get_tickets_by_assignee
from src.tools.get_ticket_status_tool import get_ticket_status
from src.tools.get_ticket_count_by_status_tool import get_ticket_count_by_status
from src.tools.get_tickets_not_updated_since_tool import get_tickets_not_updated_since
from src.tools.get_tickets_updated_by_others_tool import get_tickets_updated_by_others
from src.tools.get_tickets_with_approaching_deadlines_tool import get_tickets_with_approaching_deadlines
from src.tools.get_tickets_stagnant_in_status_tool import get_tickets_stagnant_in_status

class Orchestrator:
    """
    The orchestrator manages the overall workflow of the agentic RAG system.
    It defines the graph of agents and the transitions between them.
    """
    def __init__(self, rephraser: Rephraser, retriever: Retriever, generator: Generator, evaluator: Evaluator, intent_classifier: IntentClassifier, jira_adapter: JiraAdapter):
        self.rephraser = rephraser
        self.retriever = retriever
        self.generator = generator
        self.evaluator = evaluator
        self.intent_classifier = intent_classifier
        self.jira_adapter = jira_adapter
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
        documents = state.get('retrieved_documents', []) # Use .get for safety
        generated_answer = self.generator.generate(query, [doc.page_content for doc in documents])
        return {"generated_answer": generated_answer}

    def evaluator_node(self, state: AgentState) -> dict:
        """Node that calls the Evaluator agent."""
        print("---CALLING EVALUATOR---")
        query = state['original_query']
        documents = state.get('retrieved_documents', []) # Use .get for safety
        generated_answer = state['generated_answer']
        is_faithful = self.evaluator.evaluate(query, [doc.page_content for doc in documents], generated_answer)

        final_answer = generated_answer if is_faithful else "I cannot provide a faithful answer based on the retrieved documents."
        return {"final_answer": final_answer, "is_answer_faithful": is_faithful}

    def final_answer_node(self, state: AgentState) -> dict:
        """Node that sets the final answer without evaluation."""
        print("---CALLING FINAL ANSWER NODE---")
        generated_answer = state['generated_answer']
        return {"final_answer": generated_answer}

    def tool_executor_node(self, state: AgentState) -> dict:
        """Node that executes the appropriate Jira tool based on the intent."""
        print("---CALLING TOOL EXECUTOR---")
        intent = state['intent']
        query = state['original_query']
        result = ""

        if intent == "GET_TICKETS_BY_ASSIGNEE":
            match = re.search(r'[\w\.\-]+@[\w\.\-]+', query)
            if match:
                email = match.group(0)
                result = get_tickets_by_assignee(self.jira_adapter, email)
            else:
                result = "Could not extract email from the query."

        elif intent == "GET_TICKET_STATUS":
            match = re.search(r'([A-Z]+-\d+)', query)
            if match:
                ticket_key = match.group(0)
                result = get_ticket_status(self.jira_adapter, ticket_key)
            else:
                result = "Could not extract ticket key from the query."

        elif intent == "GET_TICKET_COUNT_BY_STATUS":
            match = re.search(r'status ["\'](.+?)["\']', query)
            if match:
                status = match.group(1)
                result = get_ticket_count_by_status(self.jira_adapter, status)
            else:
                result = "Could not extract status from the query. Please put the status in quotes."

        elif intent == "GET_TICKETS_NOT_UPDATED_SINCE":
            match = re.search(r'(\d+)\s+hours', query)
            if match:
                hours = int(match.group(1))
                result = get_tickets_not_updated_since(self.jira_adapter, hours)
            else:
                result = "Could not extract the number of hours from the query."

        elif intent == "GET_TICKETS_UPDATED_BY_OTHERS":
            match = re.search(r'[\w\.\-]+@[\w\.\-]+', query)
            if match:
                email = match.group(0)
                result = get_tickets_updated_by_others(self.jira_adapter, email)
            else:
                result = "Could not extract email from the query for GET_TICKETS_UPDATED_BY_OTHERS."

        elif intent == "GET_TICKETS_WITH_APPROACHING_DEADLINES":
            match = re.search(r'(\d+)\s+days', query)
            if match:
                days = int(match.group(1))
                result = get_tickets_with_approaching_deadlines(self.jira_adapter, days)
            else:
                result = "Could not extract the number of days from the query."

        elif intent == "GET_TICKETS_STAGNANT_IN_STATUS":
            match = re.search(r'(\d+)\s+days', query)
            if match:
                days = int(match.group(1))
                result = get_tickets_stagnant_in_status(self.jira_adapter, days)
            elif 'week' in query:
                result = get_tickets_stagnant_in_status(self.jira_adapter, 7)
            else:
                result = "Could not extract the number of days from the query."
        else:
            result = "I am sorry, I cannot handle this type of Jira query yet."

        documents = [Document(page_content=result, metadata={"source": "jira_tool"})]
        return {"retrieved_documents": documents}


    def _build_workflow(self):
        """Builds the LangGraph workflow for the agentic RAG system."""
        workflow = StateGraph(AgentState)

        workflow.add_node("intent_classifier", self.intent_classifier_node)
        workflow.add_node("rephraser", self.rephraser_node)
        workflow.add_node("retriever", self.retriever_node)
        workflow.add_node("tool_executor", self.tool_executor_node)
        workflow.add_node("generator", self.generator_node)
        workflow.add_node("evaluator", self.evaluator_node)
        workflow.add_node("final_answer", self.final_answer_node)

        workflow.set_entry_point("intent_classifier")

        def route_after_intent_classification(state):
            intent = state['intent']
            if intent == 'KNOWLEDGE_QUERY':
                return 'rephraser'
            elif intent == 'OTHER':
                return 'generator'
            else:
                return 'tool_executor'

        workflow.add_conditional_edges(
            "intent_classifier",
            route_after_intent_classification,
            {
                "rephraser": "rephraser",
                "tool_executor": "tool_executor",
                "generator": "generator",
            }
        )

        def route_after_generator(state):
            intent = state['intent']
            if intent == 'KNOWLEDGE_QUERY':
                return 'evaluator'
            else:
                return 'final_answer'

        workflow.add_conditional_edges(
            "generator",
            route_after_generator,
            {
                "evaluator": "evaluator",
                "final_answer": "final_answer",
            }
        )

        workflow.add_edge("rephraser", "retriever")
        workflow.add_edge("retriever", "generator")
        workflow.add_edge("tool_executor", "generator")
        workflow.add_edge("evaluator", END)
        workflow.add_edge("final_answer", END)

        return workflow.compile()

    def run(self, query: str):
        """Runs the JIRA agentic RAG system with the given query."""
        initial_state = {"original_query": query}
        final_state = None
        for s in self.workflow.stream(initial_state):
            print(f"---STATE UPDATE---\n{s}\n---END STATE UPDATE---")
            final_state = s
        return final_state

import unittest
from unittest.mock import MagicMock, patch
from src.agents.orchestrator import Orchestrator
from src.agents.retriever import Retriever
from src.agents.generator import Generator
from src.agents.rephraser import Rephraser
from src.agents.evaluator import Evaluator
from src.agents.intent_classifier import IntentClassifier
from src.tools.jira_adapter import JiraAdapter
from src.tools.vector_store import get_vector_store

class TestIntents(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        self.mock_jira_adapter = MagicMock(spec=JiraAdapter)
        self.vector_store = get_vector_store(collection_name="test_intents_collection")

        # Initialize agents
        self.rephraser_agent = Rephraser()
        self.retriever_agent = Retriever(vector_store=self.vector_store, jira_adapter=self.mock_jira_adapter)
        self.generator_agent = Generator()
        self.evaluator_agent = Evaluator()
        self.intent_classifier_agent = IntentClassifier()

        # Initialize orchestrator with the mocked Jira adapter
        self.orchestrator = Orchestrator(
            rephraser=self.rephraser_agent,
            retriever=self.retriever_agent,
            generator=self.generator_agent,
            evaluator=self.evaluator_agent,
            intent_classifier=self.intent_classifier_agent,
            jira_adapter=self.mock_jira_adapter
        )

    def test_get_tickets_by_assignee_intent(self):
        """Test the GET_TICKETS_BY_ASSIGNEE intent."""
        # Arrange
        query = "How many tickets are assigned to test@example.com?"
        expected_response = "User test@example.com has 5 tickets assigned."
        self.mock_jira_adapter.get_tickets_by_assignee.return_value = expected_response

        # Act
        result_state = self.orchestrator.run(query)
        final_answer = result_state.get('evaluator', {}).get('final_answer')

        # Assert
        self.assertIn("5 tickets", final_answer)

    def test_get_ticket_status_intent(self):
        """Test the GET_TICKET_STATUS intent."""
        # Arrange
        query = "What is the status of ticket PSA-123?"
        expected_response = "Ticket PSA-123 is in status: In Progress."
        self.mock_jira_adapter.get_ticket_status.return_value = expected_response

        # Act
        result_state = self.orchestrator.run(query)
        final_answer = result_state.get('evaluator', {}).get('final_answer')

        # Assert
        self.assertIn("In Progress", final_answer)

    def test_get_ticket_count_by_status_intent(self):
        """Test the GET_TICKET_COUNT_BY_STATUS intent."""
        # Arrange
        query = 'How many tickets are in status "In Progress"?'
        expected_response = "There are 10 tickets in 'In Progress' status."
        self.mock_jira_adapter.get_ticket_count_by_status.return_value = expected_response

        # Act
        result_state = self.orchestrator.run(query)
        final_answer = result_state.get('evaluator', {}).get('final_answer')

        # Assert
        self.assertIn("10 tickets", final_answer)

    def test_get_tickets_not_updated_since_intent(self):
        """Test the GET_TICKETS_NOT_UPDATED_SINCE intent."""
        # Arrange
        query = "Show me tickets not updated in the last 24 hours"
        expected_response = "Tickets not updated in the last 24 hours:\n- PSA-1: Stale ticket (Status: Open, Last Updated: 2023-10-26)"
        self.mock_jira_adapter.get_tickets_not_updated_since.return_value = expected_response

        # Act
        result_state = self.orchestrator.run(query)
        final_answer = result_state.get('evaluator', {}).get('final_answer')

        # Assert
        self.assertIn("Stale ticket", final_answer)

    def test_get_tickets_with_approaching_deadlines_intent(self):
        """Test the GET_TICKETS_WITH_APPROACHING_DEADLINES intent."""
        # Arrange
        query = "Show me tickets due in the next 5 days"
        expected_response = "Tickets with approaching deadlines (5 days):\n- PSA-2: Urgent ticket (Status: Open, Due: 2023-11-01)"
        self.mock_jira_adapter.get_tickets_with_approaching_deadlines.return_value = expected_response

        # Act
        result_state = self.orchestrator.run(query)
        final_answer = result_state.get('evaluator', {}).get('final_answer')

        # Assert
        self.assertIn("Urgent ticket", final_answer)

    def test_get_tickets_stagnant_in_status_intent(self):
        """Test the GET_TICKETS_STAGNANT_IN_STATUS intent."""
        # Arrange
        query = "Show me tickets that haven't changed status in a week"
        expected_response = "Stagnant tickets (not changed status in 7 days):\n- PSA-3: Stuck ticket (Status: In Progress, Last Status Change: 2023-10-20)"
        self.mock_jira_adapter.get_tickets_stagnant_in_status.return_value = expected_response

        # Act
        result_state = self.orchestrator.run(query)
        final_answer = result_state.get('evaluator', {}).get('final_answer')

        # Assert
        self.assertIn("Stuck ticket", final_answer)

    def test_get_tickets_updated_by_others_intent(self):
        """Test the GET_TICKETS_UPDATED_BY_OTHERS intent."""
        # Arrange
        query = "Did anyone comment on my tickets? My email is test@example.com"
        expected_response = "Tickets for test@example.com updated by others:\n- PSA-4: Another user commented on this ticket"
        self.mock_jira_adapter.get_tickets_updated_by_others.return_value = expected_response

        # Act
        result_state = self.orchestrator.run(query)
        final_answer = result_state.get('evaluator', {}).get('final_answer')

        # Assert
        self.assertIn("Another user commented", final_answer)

if __name__ == '__main__':
    unittest.main()

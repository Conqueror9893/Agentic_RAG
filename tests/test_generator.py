import pytest
from src.agents.generator import Generator
from unittest.mock import patch

def test_generator_initialization():
    """
    Tests that the Generator agent can be initialized.
    Mocks the subprocess call to avoid dependency on Ollama being installed.
    """
    with patch('subprocess.run') as mock_run:
        # Simulate a successful version check
        mock_run.return_value.returncode = 0
        generator = Generator()
        assert generator is not None
        assert generator.model_name == "openchat:latest"

def test_generator_initialization_with_custom_model():
    """
    Tests that the Generator agent can be initialized with a custom model name.
    """
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        generator = Generator(model_name="my-custom-model")
        assert generator is not None
        assert generator.model_name == "my-custom-model"

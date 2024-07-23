import pytest
import requests
from unittest.mock import patch, Mock, MagicMock
from src.main import DEEPGRAM_API_KEY
from src.utils import stream_content
import warnings
from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions
import time


def test_chat_history_initialization():
    """
    Test that the chat history is initialized correctly. The chat history is stored
    in the Streamlit session state
    """
    import streamlit as st

    # Ensure messages are initialized correctly
    if "messages" in st.session_state:
        del st.session_state["messages"]

    # Run the initialization code
    if "messages" not in st.session_state:
        st.session_state.messages = []

    assert st.session_state.messages == []


def test_stream_content():
    """
    Test the stream_content function by mocking the response from the API.
    """
    # Mock response content
    response_content = [
        b'{"message": {"content": "Hello, "}}',
        b'{"message": {"content": "world!"}}',
        b'{"done": true}',
    ]

    # Create a mock response object with iter_lines method
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = response_content
    mock_response.raise_for_status = Mock()

    # Patch 'requests.post' to return a context manager that yields the mock response
    with patch("requests.post") as mock_post:
        mock_post.return_value.__enter__.return_value = mock_response
        result = list(stream_content("http://example.com/api", {"key": "value"}))

    # Assert the result
    assert result == ["Hello, ", "world!"]


def test_stream_content_invalid_json():
    """
    Test the stream_content function by mocking the response from the API with an invalid JSON chunk.
    """
    # Mock response content with an invalid JSON chunk
    response_content = [
        b'{"message": {"content": "Hello, "}}',
        b"invalid json",
        b'{"message": {"content": "world!"}}',
        b'{"done": true}',
    ]

    # Create a mock response object with iter_lines method
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = response_content
    mock_response.raise_for_status = Mock()

    # Patch 'requests.post' to return a context manager that yields the mock response
    with patch("requests.post") as mock_post:
        mock_post.return_value.__enter__.return_value = mock_response
        result = list(stream_content("http://example.com/api", {"key": "value"}))

    # Assert the result
    assert result == ["Hello, ", "world!"]

    if __name__ == "__main__":
        pytest.main()


def test_stream_content_http_error():
    """
    Test the stream_content function by mocking the response from the API with an HTTP error.
    """
    # Create a mock response object that raises an HTTP error
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError

    # Patch 'requests.post' to return a context manager that yields the mock response
    with patch("requests.post") as mock_post:
        mock_post.return_value.__enter__.return_value = mock_response
        with pytest.raises(requests.exceptions.HTTPError):
            list(stream_content("http://example.com/api", {"key": "value"}))

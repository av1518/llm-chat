import pytest
import requests
from unittest.mock import patch, Mock, MagicMock
from src.main import stream_content


def test_stream_content():
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
    with patch("requests.post", return_value=mock_response):
        result = list(stream_content("http://example.com/api", {"key": "value"}))

    # Assert the result
    assert result == ["Hello, ", "world!"]


if __name__ == "__main__":
    pytest.main()

from unittest.mock import Mock, patch

import pytest

from services.research_corpus.sources.openalex_client import OpenAlexClient


def test_search_works_returns_results():
    client = OpenAlexClient()

    response = Mock()
    response.json.return_value = {
        "results": [
            {"id": "https://openalex.org/W123"},
            {"id": "https://openalex.org/W456"},
        ]
    }
    response.raise_for_status.return_value = None

    with patch(
        "services.research_corpus.sources.openalex_client.requests.get",
        return_value=response,
    ) as mock_get:
        results = client.search_works(
            "machine learning",
            limit=2,
        )

    assert len(results) == 2
    assert results[0]["id"] == "https://openalex.org/W123"

    mock_get.assert_called_once()

    _, kwargs = mock_get.call_args

    assert kwargs["params"]["search"] == "machine learning"
    assert kwargs["params"]["per_page"] == 2


def test_search_works_rejects_empty_query():
    client = OpenAlexClient()

    with pytest.raises(ValueError, match="query must not be empty"):
        client.search_works("")


def test_search_works_rejects_invalid_limit():
    client = OpenAlexClient()

    with pytest.raises(ValueError):
        client.search_works("machine learning", limit=0)

    with pytest.raises(ValueError):
        client.search_works("machine learning", limit=101)


def test_get_work_returns_work():
    client = OpenAlexClient()

    response = Mock()
    response.json.return_value = {
        "id": "https://openalex.org/W123",
        "display_name": "Test Paper",
    }
    response.raise_for_status.return_value = None

    with patch(
        "services.research_corpus.sources.openalex_client.requests.get",
        return_value=response,
    ):
        result = client.get_work("W123")

    assert result is not None
    assert result["display_name"] == "Test Paper"


def test_get_work_returns_none_for_404():
    client = OpenAlexClient()

    response = Mock()
    response.status_code = 404

    with patch(
        "services.research_corpus.sources.openalex_client.requests.get",
        return_value=response,
    ):
        result = client.get_work("W999")

    assert result is None


def test_get_work_rejects_empty_id():
    client = OpenAlexClient()

    with pytest.raises(ValueError, match="work_id must not be empty"):
        client.get_work("")
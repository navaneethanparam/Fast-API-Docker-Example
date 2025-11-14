import pytest
import httpx
from unittest.mock import patch, MagicMock

# 1. Import TestClient
from fastapi.testclient import TestClient

# Import the FastAPI app instance from your main.py file
from main import app, r as main_redis_client

# 2. Remove the 'pytestmark' - we don't need it anymore
# pytestmark = pytest.mark.asyncio

# We patch the 'r' (Redis client) object in main.py
# This replaces the real Redis client with a fake (MagicMock)
@pytest.fixture(autouse=True)
def mock_redis():
    """
    Mock the Redis client 'r' in main.py for all tests.
    This prevents tests from needing a real Redis server.
    """
    mock_r = MagicMock()
    mock_r.incr.return_value = 1
    with patch('main.r', mock_r):
        yield mock_r

# 3. Change the client fixture to be synchronous
@pytest.fixture
def client():
    """
    Create a synchronous test client for the FastAPI app.
    """
    # Use TestClient(app) instead of httpx.AsyncClient
    with TestClient(app) as c:
        yield c

# 4. Change 'async def' to 'def' and remove 'await'
def test_read_root(client: TestClient):
    """
    Test the root endpoint (/).
    """
    response = client.get("/")  # No await
    assert response.status_code == 200
    assert response.json() == {"message":"Hello You All DLH Students"}


# 5. Do the same for all other tests
def test_read_hits(client: TestClient, mock_redis: MagicMock):
    """
    Test the /hits endpoint, using the mocked Redis client.
    """
    response = client.get("/hits")  # No await
    
    assert response.status_code == 200
    mock_redis.incr.assert_called_once_with("hits")
    assert response.json() == {"message": "This page has been viewed", "hits": 1}

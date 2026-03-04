import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Provide a test client and reset activities before each test."""
    # Store original activities
    original_activities = copy.deepcopy(activities)
    
    yield TestClient(app)
    
    # Restore original activities after each test
    activities.clear()
    activities.update(original_activities)

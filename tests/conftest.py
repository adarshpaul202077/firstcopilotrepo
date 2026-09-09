"""
Pytest configuration and fixtures for the FastAPI activities app.
Provides TestClient, test data, and utilities following AAA pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Arrange: Provide a TestClient for making requests to the app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Arrange: Provide clean, isolated test data.
    Resets the in-memory activities dict before each test to prevent cross-test contamination.
    """
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup: restore original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def simple_activity():
    """Arrange: Provide a minimal test activity with no participants."""
    return {
        "Test Activity": {
            "description": "A simple test activity",
            "schedule": "Monday, 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
    }


@pytest.fixture
def test_email():
    """Arrange: Provide a consistent test email."""
    return "test@mergington.edu"


@pytest.fixture
def test_activity_name():
    """Arrange: Provide a consistent test activity name."""
    return "Chess Club"

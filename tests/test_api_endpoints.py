"""
Integration tests for FastAPI endpoints.
Tests all API endpoints using the Arrange-Act-Assert pattern.
"""

import pytest


@pytest.mark.integration
class TestGetActivities:
    """Test suite for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: Client ready
        Act: Request all activities
        Assert: Verify response contains all activities with correct structure
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert all(activity in data for activity in expected_activities)
    
    def test_get_activities_includes_participant_list(self, client, reset_activities):
        """
        Arrange: Client ready
        Act: Request activities
        Assert: Verify each activity has participants list
        """
        # Arrange
        # (implicit: activities fixture has data)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in data.items():
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data


@pytest.mark.integration
class TestSignUpForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_success(self, client, reset_activities, test_email):
        """
        Arrange: Empty activity, new email
        Act: Post signup request
        Assert: Participant added to list, success message returned
        """
        # Arrange
        activity_name = "Gym Class"
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        updated_activity = client.get("/activities").json()[activity_name]
        assert test_email in updated_activity["participants"]
        assert len(updated_activity["participants"]) == initial_count + 1
    
    def test_signup_duplicate_participant_rejected(self, client, reset_activities):
        """
        Arrange: Activity with existing participant
        Act: Post signup with same email twice
        Assert: Second signup rejected with 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        duplicate_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_invalid_activity_not_found(self, client, reset_activities):
        """
        Arrange: Nonexistent activity name
        Act: Post signup to invalid activity
        Assert: 404 error returned
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": "test@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """
        Arrange: Email with special characters (but valid format)
        Act: Post signup with encoded email
        Assert: Signup succeeds with properly encoded email
        """
        # Arrange
        activity_name = "Gym Class"
        special_email = "user+tag@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": special_email}
        )
        
        # Assert
        assert response.status_code == 200
        updated_activity = client.get("/activities").json()[activity_name]
        assert special_email in updated_activity["participants"]


@pytest.mark.integration
class TestRemoveFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint."""
    
    def test_remove_participant_success(self, client, reset_activities):
        """
        Arrange: Activity with existing participant
        Act: Delete request to remove participant
        Assert: Participant removed from list, success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        updated_activity = client.get("/activities").json()[activity_name]
        assert email_to_remove not in updated_activity["participants"]
        assert len(updated_activity["participants"]) == initial_count - 1
    
    def test_remove_nonexistent_participant_rejected(self, client, reset_activities):
        """
        Arrange: Activity without the specified participant
        Act: Delete request for participant not in activity
        Assert: 400 error returned
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": nonexistent_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_remove_from_invalid_activity(self, client, reset_activities):
        """
        Arrange: Nonexistent activity
        Act: Delete request from invalid activity
        Assert: 404 error returned
        """
        # Arrange
        invalid_activity = "Fake Club"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/signup",
            params={"email": "test@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_remove_then_readd_participant(self, client, reset_activities):
        """
        Arrange: Participant in activity
        Act: Remove participant, then add them back
        Assert: Both operations succeed, participant count correct
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Remove
        response_delete = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Remove succeeded
        assert response_delete.status_code == 200
        activity_after_delete = client.get("/activities").json()[activity_name]
        assert email not in activity_after_delete["participants"]
        
        # Act - Re-add
        response_add = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Re-add succeeded
        assert response_add.status_code == 200
        activity_after_readd = client.get("/activities").json()[activity_name]
        assert email in activity_after_readd["participants"]

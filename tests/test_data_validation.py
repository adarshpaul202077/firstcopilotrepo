"""
Unit tests for data validation and business logic.
Tests validation rules, edge cases, and state management using AAA pattern.
"""

import pytest


@pytest.mark.unit
class TestParticipantValidation:
    """Test suite for participant-related validation."""
    
    def test_participant_already_exists_detection(self, client, reset_activities):
        """
        Arrange: Activity with existing participant
        Act: Query activities data
        Assert: Participant is correctly present in list
        """
        # Arrange
        activity_name = "Programming Class"
        existing_email = "emma@mergington.edu"
        
        # Act
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        
        # Assert
        assert existing_email in activity_data["participants"]
    
    def test_duplicate_signup_rejected_on_resubmit(self, client, reset_activities):
        """
        Arrange: New participant signup
        Act: Submit same signup twice
        Assert: Second submission rejected, count doesn't increase
        """
        # Arrange
        activity_name = "Gym Class"
        email = "newuser@mergington.edu"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - First succeeds
        assert response1.status_code == 200
        
        # Act - Second signup (duplicate)
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Second fails
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


@pytest.mark.unit
class TestActivityValidation:
    """Test suite for activity-related validation."""
    
    def test_activity_exists_check(self, client, reset_activities):
        """
        Arrange: List of valid and invalid activity names
        Act: Attempt signup with each
        Assert: Valid activities accept, invalid ones rejected with 404
        """
        # Arrange
        valid_activity = "Chess Club"
        invalid_activity = "Nonexistent Activity"
        
        # Act & Assert - Valid activity
        response_valid = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": "test@example.com"}
        )
        assert response_valid.status_code == 200
        
        # Act & Assert - Invalid activity
        response_invalid = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": "test@example.com"}
        )
        assert response_invalid.status_code == 404
    
    def test_activity_structure_includes_required_fields(self, client, reset_activities):
        """
        Arrange: Fetch activities
        Act: Inspect activity structure
        Assert: All required fields present
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert all(field in activity_data for field in required_fields), \
                f"Activity '{activity_name}' missing required fields"


@pytest.mark.unit
class TestStateManagement:
    """Test suite for state changes and consistency."""
    
    def test_participant_count_accuracy_after_signup(self, client, reset_activities):
        """
        Arrange: Activity with known participant count
        Act: Add new participant
        Assert: Count increases by exactly 1
        """
        # Arrange
        activity_name = "Gym Class"
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "newcomer@mergington.edu"}
        )
        
        # Assert
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])
        assert count_after == count_before + 1
    
    def test_participant_count_accuracy_after_removal(self, client, reset_activities):
        """
        Arrange: Activity with known participant count
        Act: Remove participant
        Assert: Count decreases by exactly 1
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])
        
        # Act
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email_to_remove}
        )
        
        # Assert
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])
        assert count_after == count_before - 1
    
    def test_other_activities_unaffected_by_signup(self, client, reset_activities):
        """
        Arrange: Multiple activities with participant counts
        Act: Sign up for one activity
        Assert: Other activities' counts unchanged
        """
        # Arrange
        activity_to_modify = "Chess Club"
        unrelated_activity = "Programming Class"
        
        response_before = client.get("/activities")
        unrelated_count_before = len(response_before.json()[unrelated_activity]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_to_modify}/signup",
            params={"email": "newuser@mergington.edu"}
        )
        
        # Assert
        response_after = client.get("/activities")
        unrelated_count_after = len(response_after.json()[unrelated_activity]["participants"])
        assert unrelated_count_after == unrelated_count_before

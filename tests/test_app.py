import pytest


class TestGetActivities:
    def test_get_all_activities_returns_200(self, client):
        # Arrange
        expected_status = 200
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == expected_status

    def test_get_all_activities_returns_all_9_activities(self, client):
        # Arrange
        expected_activity_count = 9
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Tennis Club", "Art Studio",
            "Drama Club", "Science Club", "Debate Team"
        ]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities) == expected_activity_count
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_activity_has_required_fields(self, client):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_data in activities.values():
            assert all(field in activity_data for field in required_fields)

    def test_participants_is_list(self, client):
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_data in activities.values():
            assert isinstance(activity_data["participants"], list)


class TestRootRedirect:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_redirect_path = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "location" in response.headers
        assert response.headers["location"] == expected_redirect_path


class TestSignup:
    def test_signup_valid_activity_and_email_returns_200(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newemail@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newemail@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_activity_name_is_case_sensitive(self, client):
        # Arrange
        activity_name = "chess club"  # lowercase, should not match "Chess Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404

    def test_signup_increments_participant_count(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newemail@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        
        # Assert
        assert final_count == initial_count + 1


class TestUnregister:
    def test_unregister_valid_participant_returns_200(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_unregister_removes_participant_from_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404

    def test_unregister_decrements_participant_count(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        
        # Assert
        assert final_count == initial_count - 1


class TestSignupAndUnregisterFlow:
    def test_signup_then_unregister_removes_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newemail@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response_after_signup = client.get("/activities")
        assert email in response_after_signup.json()[activity_name]["participants"]
        
        # Act - Unregister
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        response_after_unregister = client.get("/activities")
        
        # Assert
        assert email not in response_after_unregister.json()[activity_name]["participants"]

    def test_can_signup_again_after_unregister(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newemail@mergington.edu"
        
        # Act - Sign up
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Unregister
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        
        # Act - Sign up again
        response2 = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

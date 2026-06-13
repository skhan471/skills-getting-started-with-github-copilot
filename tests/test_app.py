import pytest
from copy import deepcopy
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_root_redirects_to_static_index():
    response = client.get("/")

    assert response.status_code == 200
    assert response.url.path.endswith("/static/index.html")


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_participant():
    activity_name = "Tennis Team"
    email = "alex@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_invalid_activity_returns_404():
    response = client.post("/activities/Nonexistent/signup", params={"email": "alex@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_when_already_registered_returns_400():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_removes_participant():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_activity_not_registered_returns_400():
    activity_name = "Tennis Team"
    email = "alex@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"

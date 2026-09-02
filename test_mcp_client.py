import requests
import json
from datetime import datetime, timezone
import time # Added for sleep

BASE_URL = "http://127.0.0.1:8001/contexts" # MCP server runs on port 8001
TEST_CONTEXT_ID = "test_user_123_session_abc"

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        # Ensure proper JSON formatting in the printout for readability
        print(json.dumps(response.json(), indent=2, default=str))
    except json.JSONDecodeError:
        print("Response Text:")
        print(response.text)
    print("-" * 30)

def test_set_context():
    print(f"--- Testing PUT {BASE_URL}/{TEST_CONTEXT_ID} ---")
    payload = {
        "modelId": "test_model_v1",
        "userId": "test_user_123",
        "contextData": {
            "current_task": "reading_comprehension",
            "difficulty": "medium",
            "history": ["event1", "event2"]
        }
    }
    response = requests.put(f"{BASE_URL}/{TEST_CONTEXT_ID}", json=payload)
    print_response(response)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["contextId"] == TEST_CONTEXT_ID, "Context ID mismatch"
    assert data["contextData"]["current_task"] == "reading_comprehension", "Task data mismatch"
    return data

def test_get_context():
    print(f"--- Testing GET {BASE_URL}/{TEST_CONTEXT_ID} ---")
    response = requests.get(f"{BASE_URL}/{TEST_CONTEXT_ID}")
    print_response(response)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["contextId"] == TEST_CONTEXT_ID, "Context ID mismatch"
    assert data["contextData"]["difficulty"] == "medium", "Difficulty data mismatch"
    return data

def test_get_nonexistent_context():
    print(f"--- Testing GET {BASE_URL}/nonexistent_context ---")
    response = requests.get(f"{BASE_URL}/nonexistent_context")
    print_response(response)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_update_context(initial_timestamp_str):
    print(f"--- Testing PUT (Update) {BASE_URL}/{TEST_CONTEXT_ID} ---")
    payload = {
        "modelId": "test_model_v1_updated",
        "userId": "test_user_123",
        "contextData": {
            "current_task": "vocabulary_test",
            "difficulty": "hard",
            "history": ["event1", "event2", "event3"],
            "new_field": "some_value"
        }
    }
    # Brief pause to ensure timestamp will be different
    time.sleep(0.05) # Increased sleep time slightly
    response = requests.put(f"{BASE_URL}/{TEST_CONTEXT_ID}", json=payload)
    print_response(response)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["contextId"] == TEST_CONTEXT_ID, "Context ID mismatch on update"
    assert data["contextData"]["current_task"] == "vocabulary_test", "Task data mismatch on update"
    assert data["contextData"]["new_field"] == "some_value", "New field mismatch on update"

    # Pydantic model in server now automatically handles ISO format with timezone
    # Ensure initial_timestamp_str is parsed correctly, assuming it might or might not have Z
    if initial_timestamp_str.endswith('Z'):
        initial_timestamp_str = initial_timestamp_str[:-1] + "+00:00"
    initial_dt = datetime.fromisoformat(initial_timestamp_str)

    if data["lastUpdated"].endswith('Z'):
        updated_timestamp_str = data["lastUpdated"][:-1] + "+00:00"
    else:
        updated_timestamp_str = data["lastUpdated"]
    updated_dt = datetime.fromisoformat(updated_timestamp_str)

    # Ensure they are both offset-aware for comparison
    if initial_dt.tzinfo is None:
        initial_dt = initial_dt.replace(tzinfo=timezone.utc)
    if updated_dt.tzinfo is None:
        updated_dt = updated_dt.replace(tzinfo=timezone.utc)

    assert updated_dt > initial_dt, f"Updated timestamp {updated_dt} not greater than initial {initial_dt}"
    print(f"Initial Timestamp: {initial_timestamp_str}, Updated Timestamp: {data['lastUpdated']}")


def test_delete_context():
    print(f"--- Testing DELETE {BASE_URL}/{TEST_CONTEXT_ID} ---")
    response = requests.delete(f"{BASE_URL}/{TEST_CONTEXT_ID}")
    print_response(response)
    # The FastAPI app returns the deleted item with 200, not 204
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    print(f"--- Verifying DELETE by GET {BASE_URL}/{TEST_CONTEXT_ID} ---")
    getResponse = requests.get(f"{BASE_URL}/{TEST_CONTEXT_ID}")
    print_response(getResponse)
    assert getResponse.status_code == 404, f"Expected 404 after delete, got {getResponse.status_code}"

def test_delete_nonexistent_context():
    print(f"--- Testing DELETE {BASE_URL}/nonexistent_context_del ---")
    response = requests.delete(f"{BASE_URL}/nonexistent_context_del")
    print_response(response)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

if __name__ == "__main__":
    print("Starting MCP Server API Tests...")
    created_context = test_set_context()
    retrieved_context = test_get_context()

    assert created_context["lastUpdated"] == retrieved_context["lastUpdated"], \
        f"Timestamp mismatch: {created_context['lastUpdated']} vs {retrieved_context['lastUpdated']}"
    print(f"Timestamp consistency for initial set/get: {created_context['lastUpdated']}")

    test_get_nonexistent_context()
    test_update_context(created_context["lastUpdated"])
    test_delete_context()
    test_delete_nonexistent_context()
    print("MCP Server API Tests Completed Successfully!")

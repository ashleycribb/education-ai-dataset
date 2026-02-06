import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Set environment variable for DB before importing app to ensure Config picks it up
# or at least before db connects.
os.environ['FLASK_DATABASE_URL'] = 'sqlite:///:memory:'

# Assuming we run this from the repo root as: python3 -m lms_frontend_flask.test_api_routes
from lms_frontend_flask.app import app, db

class TestAPIRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_start_ai_activity_api(self):
        response = self.client.post('/api/activity/start', json={
            "user_id": "test_user",
            "activity_key": "test_activity"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("session_id", data)
        self.assertEqual(data["status"], "AI activity started")

    @patch('lms_frontend_flask.app.requests.post')
    def test_interact_ai_activity_api_success(self, mock_post):
        # Mock response from AITA service
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "session_id": "session_123",
            "aita_response": "Hello, student!",
            "debug_info": {}
        }
        mock_post.return_value = mock_response

        payload = {
            "session_id": "session_123",
            "user_id": "test_user",
            "user_utterance": "Hello AI",
            "ai_activity_key": "test_activity"
        }

        response = self.client.post('/api/activity/interact', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("ai_messages", data)
        self.assertEqual(data["ai_messages"][0], "Hello, student!")
        self.assertEqual(data["session_id"], "session_123")

    @patch('lms_frontend_flask.app.requests.post')
    def test_interact_ai_activity_api_failure(self, mock_post):
        # Mock connection error
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Connection refused")

        payload = {
            "session_id": "session_123",
            "user_id": "test_user",
            "user_utterance": "Hello AI",
            "ai_activity_key": "test_activity"
        }

        response = self.client.post('/api/activity/interact', json=payload)
        # Should return 500
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

    def test_interact_ai_activity_api_missing_data(self):
        response = self.client.post('/api/activity/interact', json={})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()

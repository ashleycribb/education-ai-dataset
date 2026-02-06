import unittest
import sys
import os

# Set environment variable BEFORE importing app to use SQLite for testing
os.environ['FLASK_DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key'

from lms_frontend_flask.app import app
from lms_frontend_flask.extensions import db
from lms_frontend_flask.models import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            user = User(username='testuser', is_admin=False)
            user.set_password('password')
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin')
            db.session.add(user)
            db.session.add(admin)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_login_logout(self):
        # Test valid login
        response = self.app.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Learning Platform!', response.data)

        # Test logout
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Learning Platform!', response.data)

    def test_admin_access_denied_for_user(self):
        # Login as non-admin
        self.app.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)

        # Try to access admin view
        response = self.app.get('/admin/course/', follow_redirects=True)
        # Should redirect to home because /login redirects to home if already authenticated
        self.assertIn(b'Welcome to the Learning Platform!', response.data)

    def test_admin_access_granted_for_admin(self):
        # Login as admin
        self.app.post('/login', data=dict(
            username='admin',
            password='admin'
        ), follow_redirects=True)

        # Try to access admin view
        response = self.app.get('/admin/course/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'List', response.data)

    def test_unauthenticated_access(self):
        # Try to access admin view without login
        response = self.app.get('/admin/course/', follow_redirects=True)
        # Should redirect to login page
        self.assertIn(b'Login', response.data)
        self.assertIn(b'Username:', response.data)

if __name__ == '__main__':
    unittest.main()

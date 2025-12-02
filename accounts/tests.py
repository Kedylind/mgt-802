"""
Tests for accounts app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def test_create_user(self):
        """Test creating a new user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class AuthenticationTest(TestCase):
    """Test cases for authentication views."""
    
    def test_signup_view(self):
        """Test user registration."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'signup')
    
    def test_login_view(self):
        """Test login view."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')


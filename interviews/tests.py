"""
Tests for interviews app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import InterviewSession, Message

User = get_user_model()


class InterviewSessionModelTest(TestCase):
    """Test cases for InterviewSession model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_interview_session(self):
        """Test creating an interview session."""
        session = InterviewSession.objects.create(
            user=self.user,
            mode=InterviewSession.INTERVIEWER_LED
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.mode, InterviewSession.INTERVIEWER_LED)
        self.assertEqual(session.status, 'not_started')


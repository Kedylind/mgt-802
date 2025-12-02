"""
Tests for analysis app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from interviews.models import InterviewSession
from .models import Recording, Evaluation

User = get_user_model()


class RecordingModelTest(TestCase):
    """Test cases for Recording model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = InterviewSession.objects.create(
            user=self.user,
            mode=InterviewSession.INTERVIEWER_LED
        )
    
    def test_create_recording(self):
        """Test creating a recording."""
        recording = Recording.objects.create(
            session=self.session,
            file_type='video'
        )
        self.assertEqual(recording.session, self.session)
        self.assertEqual(recording.file_type, 'video')


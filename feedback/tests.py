"""
Tests for feedback app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from interviews.models import InterviewSession
from analysis.models import Evaluation
from .models import Feedback

User = get_user_model()


class FeedbackModelTest(TestCase):
    """Test cases for Feedback model."""
    
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
        self.evaluation = Evaluation.objects.create(
            session=self.session,
            overall_score=75
        )
    
    def test_create_feedback(self):
        """Test creating feedback."""
        feedback = Feedback.objects.create(
            evaluation=self.evaluation,
            summary='Good performance overall',
            strengths=['Strong structure'],
            areas_for_improvement=['Math accuracy'],
            recommendations=['Practice mental math']
        )
        self.assertEqual(feedback.evaluation, self.evaluation)
        self.assertEqual(feedback.summary, 'Good performance overall')

